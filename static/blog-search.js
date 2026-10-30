// Search over the blog's posts, on the blog index page.
//
// The index is rssite's own: [search] in rssite.toml writes <lang>/search.json
// with every post's title, opening text (description) and tags, newest first.
// It is fetched the first time the reader focuses or types in the box, so a
// visit that never searches costs nothing. Matching is a plain substring test
// of every word of the query, case- and diacritic-insensitive (niqqud too), so
// it needs no stemmer and works the same in English and Hebrew.
//
// The query is kept in ?q= so a search can be linked to and survives a reload.
(function () {
    'use strict';

    const form = document.getElementById('blog-search');
    if (!form) return;
    const input = document.getElementById('blog-search-input');
    const status = document.getElementById('blog-search-status');
    const results = document.getElementById('blog-search-results');
    const listing = document.getElementById('blog-posts-listing');
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
                            rest: normalize((page.description || '') + ' ' + tags.join(' ')),
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

    // Every word must match somewhere; posts that match a word in the title
    // come first, and within each group the index's newest-first order holds.
    function search(query) {
        const words = normalize(query).split(/\s+/).filter(Boolean);
        const inTitle = [];
        const elsewhere = [];
        posts.forEach(function (post) {
            let titleHit = false;
            const all = words.every(function (word) {
                if (post.title.includes(word)) { titleHit = true; return true; }
                return post.rest.includes(word);
            });
            if (all) (titleHit ? inTitle : elsewhere).push(post);
        });
        return inTitle.concat(elsewhere);
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
        window.history.replaceState(null, '', url);

        if (!query) {
            results.hidden = true;
            results.replaceChildren();
            status.textContent = '';
            listing.hidden = false;
            return;
        }
        load().then(function () {
            // A stale call, or the index failed to load: leave things as they are.
            if (!posts || input.value.trim() !== query) return;
            const found = search(query);
            if (found.length === 0) status.textContent = form.dataset.none;
            else if (found.length === 1) status.textContent = form.dataset.foundOne;
            else status.textContent = form.dataset.found.replace('{n}', found.length);
            results.replaceChildren.apply(results, found.map(renderPost));
            results.hidden = false;
            listing.hidden = true;
        });
    }

    form.addEventListener('submit', function (event) { event.preventDefault(); });
    input.addEventListener('focus', load, { once: true });
    input.addEventListener('input', update);
    input.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && input.value) {
            input.value = '';
            update();
        }
    });

    // Shown only now: without JavaScript the box could not do anything.
    form.hidden = false;
    const initial = new URLSearchParams(window.location.search).get('q');
    if (initial) {
        input.value = initial;
        update();
    }
})();
