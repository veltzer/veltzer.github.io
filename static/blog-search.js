// Search over the blog's posts, on the blog index page.
//
// The index is rssite's own: [search] in rssite.toml writes <lang>/search.json
// with every post's title, opening text (description), tags and full text
// (content), newest first.
// It is fetched the first time the reader focuses or types in the box, so a
// visit that never searches costs nothing.
//
// Three modes, search_mode and search_modes under [extra] in rssite.toml
// choosing the one a reader starts in and the ones the selector offers:
//
// - simple: every word of the query is a substring of the title, the opening
//   text or the tags;
// - full: the same, over the full text too;
// - semantic: posts ranked by meaning. Every word has a vector (fastText,
//   trained on Wikipedia by github.com/veltzer/embeddings, trimmed for the
//   site by scripts/make_word_vectors.py into data/vectors/); a post is the
//   IDF-weighted average of its words' vectors, its title counting three
//   times, a query is averaged the same way, and posts rank by cosine. So
//   "does morality need god" finds the Euthyphro post without sharing a word
//   with it. The vectors (~6 MB English, ~11 MB Hebrew) are fetched only once
//   the box is used in this mode.
//
// The substring modes are case- and diacritic-insensitive (niqqud too), so
// they need no stemmer and work the same in English and Hebrew.
//
// The query is kept in ?q=, and a mode other than the default in ?mode=, so a
// search can be linked to and survives a reload.
(function () {
    'use strict';

    const form = document.getElementById('blog-search');
    if (!form) return;
    const input = document.getElementById('blog-search-input');
    const status = document.getElementById('blog-search-status');
    const results = document.getElementById('blog-search-results');
    const listing = document.getElementById('blog-posts-listing');
    const modeSelect = document.getElementById('blog-search-mode');
    const defaultMode = form.dataset.mode;
    const lang = document.documentElement.lang;
    // The same dates the listing shows (date_format in rssite.toml): "2 Sep
    // 2026" and "2 בספטמבר 2026". Assembled from parts because en-GB spells
    // the short month "Sept" and en-US puts the day after the month.
    const dateParts = new Intl.DateTimeFormat(lang === 'he' ? 'he-IL' : 'en-US', {
        day: 'numeric', month: lang === 'he' ? 'long' : 'short', year: 'numeric', timeZone: 'UTC',
    });
    const dateFormat = {
        format: function (date) {
            const part = {};
            dateParts.formatToParts(date).forEach(function (p) { part[p.type] = p.value; });
            return lang === 'he'
                ? part.day + ' ב' + part.month + ' ' + part.year
                : part.day + ' ' + part.month + ' ' + part.year;
        },
    };

    let posts = null;
    let loading = null;
    let semantic = null;
    let semanticLoading = null;
    const params = new URLSearchParams(window.location.search);
    let mode = params.get('mode') || defaultMode;
    if (!Array.from(modeSelect.options).some(function (o) { return o.value === mode; })) mode = defaultMode;
    modeSelect.value = mode;

    // How many posts a semantic search shows: it ranks every post, so the
    // count is a choice, not a result.
    const SEMANTIC_RESULTS = 10;
    const TITLE_WEIGHT = 3;

    // Lowercase and drop combining marks: "Café" finds "cafe", and pointed
    // Hebrew (with niqqud) finds unpointed.
    function normalize(text) {
        return text.normalize('NFD').replace(/[̀-֑ͯ-ׇ]/g, '').toLowerCase();
    }

    function load() {
        if (!loading) {
            loading = fetch(form.dataset.index)
                .then(function (response) {
                    if (!response.ok) throw new Error(response.status);
                    return response.json();
                })
                .then(function (data) {
                    posts = data.pages.map(function (page) {
                        const tags = (page.taxonomies && page.taxonomies.tags) || [];
                        return {
                            page: page,
                            tags: tags,
                            title: normalize(page.title),
                            summary: normalize([page.description || '', tags.join(' ')].join(' ')),
                            content: normalize(page.content || ''),
                        };
                    });
                })
                .catch(function () {
                    loading = null;
                    status.textContent = form.dataset.error;
                });
        }
        return loading;
    }

    // The word vectors' own tokenizer: what tokenize() in the embeddings
    // repo's scripts/common.py does (and make_word_vectors.py, which says so),
    // since the vectors are keyed by it. Compatibility-decompose, fold the
    // Hebrew geresh and gershayim and the typographic apostrophe, drop every
    // combining mark, lowercase (Python casefolds, which differs only for the
    // likes of ß), and take runs of letters, an apostrophe or a double quote
    // allowed between them (don't, צה"ל). Digits are not words.
    const WORD = /[\p{L}\p{Nl}\p{No}]+(?:['"][\p{L}\p{Nl}\p{No}]+)*/gu;
    function tokenize(text) {
        return text.replace(/׳|’/g, '\'').replace(/״/g, '"')
            .normalize('NFKD').replace(/\p{Mn}/gu, '').toLowerCase()
            .match(WORD) || [];
    }

    function counts(words, weight, into) {
        words.forEach(function (word) { into.set(word, (into.get(word) || 0) + weight); });
        return into;
    }

    function fetchOk(url) {
        return fetch(url).then(function (response) {
            if (!response.ok) throw new Error(url + ': ' + response.status);
            return response;
        });
    }

    // The vectors and, from them and the index, a unit vector per post.
    function loadSemantic() {
        if (!semanticLoading) {
            semanticLoading = Promise.all([
                fetchOk(form.dataset.words).then(function (r) { return r.json(); }),
                fetchOk(form.dataset.rows).then(function (r) { return r.arrayBuffer(); }),
                fetchOk(form.dataset.scale).then(function (r) { return r.arrayBuffer(); }),
                load(),
            ]).then(function (parts) {
                if (!posts) throw new Error('no index');
                const words = parts[0];
                const table = {
                    index: new Map(words.map(function (word, i) { return [word, i]; })),
                    rows: new Int8Array(parts[1]),
                    scale: new Float32Array(parts[2]),
                };
                table.dim = table.rows.length / words.length;
                const documents = posts.map(function (post) {
                    return counts(tokenize(post.page.title), TITLE_WEIGHT,
                        counts(tokenize(post.page.content || ''), 1, new Map()));
                });
                const df = new Map();
                documents.forEach(function (doc) { counts(Array.from(doc.keys()), 1, df); });
                const idf = new Map();
                df.forEach(function (n, word) { idf.set(word, Math.log(documents.length / n)); });
                semantic = {
                    table: table,
                    idf: idf,
                    // A query word no post contains is as rare as can be.
                    rare: Math.log(documents.length),
                };
                semantic.vectors = documents.map(embed);
            }).catch(function () {
                semanticLoading = null;
                status.textContent = form.dataset.error;
            });
        }
        return semanticLoading;
    }

    // The IDF-weighted sum of the vectors of the words in doc (word -> count),
    // at unit length; null when none of them has a vector.
    function embed(doc) {
        const t = semantic.table;
        const total = new Float32Array(t.dim);
        let any = false;
        doc.forEach(function (count, word) {
            const row = t.index.get(word);
            if (row === undefined) return;
            any = true;
            const weight = count * (semantic.idf.has(word) ? semantic.idf.get(word) : semantic.rare) * t.scale[row];
            const base = row * t.dim;
            for (let j = 0; j < t.dim; j++) total[j] += weight * t.rows[base + j];
        });
        let norm = 0;
        for (let j = 0; j < t.dim; j++) norm += total[j] * total[j];
        if (!any || norm === 0) return null;
        norm = Math.sqrt(norm);
        for (let j = 0; j < t.dim; j++) total[j] /= norm;
        return total;
    }

    // The posts closest to the query in meaning; null when no word of the
    // query has a vector.
    function searchSemantic(query) {
        const q = embed(counts(tokenize(query), 1, new Map()));
        if (!q) return null;
        const scored = [];
        semantic.vectors.forEach(function (v, i) {
            if (!v) return;
            let dot = 0;
            for (let j = 0; j < q.length; j++) dot += q[j] * v[j];
            scored.push({ post: posts[i], score: dot });
        });
        scored.sort(function (a, b) { return b.score - a.score; });
        return scored.slice(0, SEMANTIC_RESULTS).map(function (s) { return s.post; });
    }

    // Every word must match somewhere (the full text too when full is true);
    // posts that match a word in the title come first, and within each group
    // the index's newest-first order holds.
    function searchText(query, full) {
        const words = normalize(query).split(/\s+/).filter(Boolean);
        const inTitle = [];
        const elsewhere = [];
        posts.forEach(function (post) {
            let titleHit = false;
            const all = words.every(function (word) {
                if (post.title.includes(word)) { titleHit = true; return true; }
                return post.summary.includes(word) || (full && post.content.includes(word));
            });
            if (all) (titleHit ? inTitle : elsewhere).push(post);
        });
        return inTitle.concat(elsewhere);
    }

    // What the current mode needs loaded before it can search.
    function ready() {
        return mode === 'semantic' ? loadSemantic() : load();
    }

    function renderPost(post) {
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.className = 'post-link';
        link.href = post.page.path;
        link.textContent = post.page.title;
        li.appendChild(link);
        const time = document.createElement('time');
        time.dateTime = post.page.date;
        time.textContent = dateFormat.format(new Date(post.page.date));
        li.appendChild(time);
        if (post.tags.length) {
            const tags = document.createElement('span');
            tags.className = 'post-tags';
            post.tags.forEach(function (name) {
                const tag = document.createElement('span');
                tag.className = 'tag';
                tag.textContent = name;
                tags.appendChild(tag);
            });
            li.appendChild(tags);
        }
        if (post.page.description) {
            const summary = document.createElement('p');
            summary.className = 'post-summary';
            summary.textContent = post.page.description;
            li.appendChild(summary);
        }
        return li;
    }

    function update() {
        const query = input.value.trim();
        const url = new URL(window.location.href);
        if (query) url.searchParams.set('q', query);
        else url.searchParams.delete('q');
        if (mode !== defaultMode) url.searchParams.set('mode', mode);
        else url.searchParams.delete('mode');
        window.history.replaceState(null, '', url);

        if (!query) {
            results.hidden = true;
            results.replaceChildren();
            status.textContent = '';
            listing.hidden = false;
            return;
        }
        const searchMode = mode;
        if (searchMode === 'semantic' && !semantic) status.textContent = form.dataset.loading;
        ready().then(function () {
            // A stale call, or the data failed to load: leave things as they are.
            if (input.value.trim() !== query || mode !== searchMode) return;
            if (searchMode === 'semantic' ? !semantic : !posts) return;
            const found = searchMode === 'semantic' ? searchSemantic(query) : searchText(query, searchMode === 'full');
            if (found === null) status.textContent = form.dataset.unknown;
            else if (searchMode === 'semantic') status.textContent = form.dataset.closest.replace('{n}', found.length);
            else if (found.length === 0) status.textContent = form.dataset.none;
            else if (found.length === 1) status.textContent = form.dataset.foundOne;
            else status.textContent = form.dataset.found.replace('{n}', found.length);
            results.replaceChildren.apply(results, (found || []).map(renderPost));
            results.hidden = false;
            listing.hidden = true;
        });
    }

    form.addEventListener('submit', function (event) { event.preventDefault(); });
    input.addEventListener('focus', ready, { once: true });
    modeSelect.addEventListener('change', function () {
        mode = modeSelect.value;
        ready();
        update();
    });
    input.addEventListener('input', update);
    input.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && input.value) {
            input.value = '';
            update();
        }
    });

    // Shown only now: without JavaScript the box could not do anything.
    form.hidden = false;
    const initial = params.get('q');
    if (initial) {
        input.value = initial;
        update();
    }
})();
