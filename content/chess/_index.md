+++
title = "Chess Viewer"
template = "chess.html"
+++

<script src="/vendor/chess.min.js"></script>

<div class="chess-viewer">
  <p id="gamePlayers" class="chess-players">Loading games…</p>
  <p id="gameCounter" class="chess-counter">&nbsp;</p>

  <div id="chessStats" class="chess-stats"></div>

  <div class="chess-picker">
    <label class="visually-hidden" for="gameSearch">Search games</label>
    <input type="search" id="gameSearch" class="chess-search"
           placeholder="Search by player, event or year…" autocomplete="off">
    <label class="visually-hidden" for="yearSelect">Year</label>
    <select id="yearSelect" class="chess-select chess-select--year"></select>
    <label class="visually-hidden" for="gameSelect">Game</label>
    <select id="gameSelect" class="chess-select"></select>
  </div>

  <div class="chess-picker">
    <label class="chess-jump-label" for="gameJump">Go to game</label>
    <input type="number" id="gameJump" class="chess-jump" min="1" step="1"
           inputmode="numeric" autocomplete="off">
    <span id="jumpRange" class="chess-jump-range"></span>
  </div>

  <div id="gameBoard" class="chess-board"></div>

  <div class="chess-controls">
    <button id="btnPrev" class="chess-btn" aria-label="Go to previous move">&larr; Move</button>
    <button id="btnNext" class="chess-btn" aria-label="Go to next move">Move &rarr;</button>
  </div>

  <div class="chess-controls">
    <button id="btnPrevGame" class="chess-btn chess-btn--game" aria-label="Go to previous game">&laquo; Game</button>
    <button id="btnNextGame" class="chess-btn chess-btn--game" aria-label="Go to next game">Game &raquo;</button>
  </div>

  <div id="status" class="chess-status"></div>
</div>

<script type="module">
// cm-chessboard 8.x is ESM-only with relative imports, so this has to be a
// module. Modules are deferred, so the DOM is ready without window.onload.
import {Chessboard, FEN} from "/vendor/cm-chessboard/src/Chessboard.js";

(function () {
    const DATA_URL = "/data/games.pgn.gz";
    // The archive is ~16,000 games / 8.8MB uncompressed. Parsing every one with
    // chess.js up front would take far too long, so the file is split into game
    // texts and only the headers are read eagerly; the moves of a game are
    // parsed the first time it is opened.
    const MAX_OPTIONS = 300;   // how many games to put in the <select> at once
    // Whose games these are. Results are recorded as 1-0 / 0-1, so a win/loss
    // record is only meaningful once you know which colour was played.
    const ME = 'veltzer';

    const titleEl = document.getElementById('gameTitle');
    const playersEl = document.getElementById('gamePlayers');
    const counterEl = document.getElementById('gameCounter');
    const statusEl = document.getElementById('status');
    const statsEl = document.getElementById('chessStats');
    const searchEl = document.getElementById('gameSearch');
    const selectEl = document.getElementById('gameSelect');
    const yearEl = document.getElementById('yearSelect');
    const jumpEl = document.getElementById('gameJump');
    const jumpRangeEl = document.getElementById('jumpRange');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const btnPrevGame = document.getElementById('btnPrevGame');
    const btnNextGame = document.getElementById('btnNextGame');

    let board = null;
    let games = [];        // {white, black, event, date, year, text, moves|null}
    let filtered = [];     // indices into games
    let currentGame = 0;   // index into filtered
    let currentMove = 0;
    let windowStart = 0;   // first entry of the <select>'s window, into filtered

    function headerValue(text, key) {
        const match = text.match(new RegExp('\\[' + key + ' "([^"]*)"'));
        return match ? match[1] : '';
    }

    function splitGames(pgn) {
        // A game starts at an [Event line that follows a blank line (or the very
        // start of the file). Splitting on that keeps each game's headers and
        // movetext together.
        const chunks = pgn.split(/\n\s*\n(?=\[Event )/);
        const out = [];
        for (const chunk of chunks) {
            const text = chunk.trim();
            if (!text.startsWith('[Event ')) continue;
            const date = headerValue(text, 'Date');
            out.push({
                white: headerValue(text, 'White') || 'White',
                black: headerValue(text, 'Black') || 'Black',
                event: headerValue(text, 'Event') || 'Game',
                result: headerValue(text, 'Result'),
                // Lower-cased once here so the win/loss tally does not have to
                // case-fold 16,000 names on every render.
                whiteIsMe: (headerValue(text, 'White') || '').toLowerCase() === ME,
                date: date,
                year: (date.match(/^(\d{4})/) || [])[1] || '',
                text: text,
                moves: null
            });
        }
        return out;
    }

    function renderStats(list) {
        let wins = 0, losses = 0, draws = 0, unfinished = 0, asWhite = 0;
        let earliest = '', latest = '';
        const opponents = new Set();
        for (const game of list) {
            if (game.whiteIsMe) { asWhite++; opponents.add(game.black); }
            else { opponents.add(game.white); }
            if (game.result === '1/2-1/2') draws++;
            else if (game.result === '1-0') { if (game.whiteIsMe) wins++; else losses++; }
            else if (game.result === '0-1') { if (game.whiteIsMe) losses++; else wins++; }
            else unfinished++;
            if (game.year) {
                if (!earliest || game.year < earliest) earliest = game.year;
                if (!latest || game.year > latest) latest = game.year;
            }
        }
        const decided = wins + losses + draws;
        const score = decided ? Math.round(((wins + draws / 2) / decided) * 100) : 0;
        const cells = [
            ['Games', list.length.toLocaleString()],
            ['Won', wins.toLocaleString()],
            ['Lost', losses.toLocaleString()],
            ['Drawn', draws.toLocaleString()],
            ['Score', score + '%'],
            ['As white', asWhite.toLocaleString()],
            ['Opponents', opponents.size.toLocaleString()],
            ['Years', earliest && latest ? (earliest === latest ? earliest : earliest + '\u2013' + latest) : '\u2013']
        ];
        statsEl.innerHTML = cells.map(function (cell) {
            return '<div class="chess-stat"><span class="chess-stat-value">' + cell[1] +
                   '</span><span class="chess-stat-label">' + cell[0] + '</span></div>';
        }).join('');
    }

    function label(game, index) {
        const year = game.year ? ' (' + game.year + ')' : '';
        return (index + 1) + '. ' + game.white + ' vs ' + game.black + year;
    }

    function movesOf(game) {
        if (game.moves) return game.moves;
        const chess = new Chess();
        // chess.js will not accept header lines that start with whitespace, and
        // needs a blank line between the headers and the movetext.
        // Two things chess.js will not accept: header lines that start with
        // whitespace, and PGN "escape" lines beginning with % -- which 3,150 of
        // these games carry (the ICS server wrote %eboard:clock and
        // %eboard:clue records between the headers and the movetext). They are
        // legal PGN but load_pgn() simply returns false, which showed as "this
        // game has no readable moves" on nearly a fifth of the archive.
        const clean = game.text.split('\n').map(function (line) {
            return line.trim();
        }).filter(function (line) {
            return !line.startsWith('%');
        }).join('\n');
        game.moves = chess.load_pgn(clean) ? chess.history({verbose: true}) : [];
        return game.moves;
    }

    // The <select> holds a MAX_OPTIONS-sized window of the filtered list rather
    // than always the first MAX_OPTIONS. Without a window, jumping to game 666
    // could not work at all: the option simply would not exist in the DOM.
    // windowStart is the index into `filtered` of the window's first entry.
    function windowFor(index) {
        if (filtered.length <= MAX_OPTIONS) return 0;
        // Centre the window on the target, then clamp to the ends of the list.
        const half = Math.floor(MAX_OPTIONS / 2);
        return Math.max(0, Math.min(index - half, filtered.length - MAX_OPTIONS));
    }

    function renderOptions() {
        const shown = filtered.slice(windowStart, windowStart + MAX_OPTIONS);
        selectEl.innerHTML = shown.map(function (gameIndex, position) {
            // The option value is the absolute index into `filtered`, so the
            // handler does not have to know where the window happens to start.
            return '<option value="' + (windowStart + position) + '">' +
                   label(games[gameIndex], windowStart + position) + '</option>';
        }).join('');
        const hidden = filtered.length - shown.length;
        counterEl.textContent = filtered.length.toLocaleString() + ' games' +
            (hidden > 0
                ? ' (showing ' + (windowStart + 1).toLocaleString() + '–' +
                  (windowStart + shown.length).toLocaleString() + ')'
                : '');
        jumpEl.max = String(filtered.length);
        jumpRangeEl.textContent = filtered.length
            ? 'of ' + filtered.length.toLocaleString()
            : '';
    }

    // Years present in the archive, newest first, built once from the parsed
    // headers rather than hardcoded -- the archive gains games over time.
    function renderYears() {
        const years = Array.from(new Set(games.map(function (g) { return g.year; })))
            .filter(Boolean).sort().reverse();
        yearEl.innerHTML = '<option value="">All years</option>' +
            years.map(function (y) {
                return '<option value="' + y + '">' + y + '</option>';
            }).join('');
    }

    function render() {
        const game = games[filtered[currentGame]];
        if (!game) return;
        const moves = movesOf(game);
        const move = moves[currentMove - 1];

        titleEl.textContent = game.event + (game.year ? ' (' + game.year + ')' : '');
        playersEl.textContent = game.white + ' vs. ' + game.black +
            (game.result ? '  ' + game.result : '');
        selectEl.value = String(currentGame);
        jumpEl.value = String(currentGame + 1);

        statusEl.textContent = moves.length
            ? 'Move ' + currentMove + ': ' + (move ? move.san : 'Start')
            : 'This game has no readable moves.';

        // Replay from the start rather than tracking incremental state: it
        // cannot drift out of sync with the move index.
        const position = new Chess();
        moves.slice(0, currentMove).forEach(function (m) { position.move(m.san); });
        board.setPosition(position.fen(), true);

        btnPrev.disabled = currentMove === 0;
        btnNext.disabled = currentMove >= moves.length;
        btnPrevGame.disabled = currentGame === 0;
        btnNextGame.disabled = currentGame >= filtered.length - 1;
    }

    function selectGame(index) {
        currentGame = index;
        currentMove = 0;      // always open a game at its starting position
        // Re-window when the target is outside the options currently in the
        // DOM, so <select> always has an entry to show as selected.
        if (index < windowStart || index >= windowStart + MAX_OPTIONS) {
            windowStart = windowFor(index);
            renderOptions();
        }
        render();
    }

    function applyFilter(query) {
        const needle = query.trim().toLowerCase();
        const year = yearEl.value;
        filtered = [];
        for (let i = 0; i < games.length; i++) {
            const g = games[i];
            // Year and text are separate axes and both must match, so picking
            // 2004 and typing an opponent's name narrows to that pairing.
            if (year && g.year !== year) continue;
            if (!needle) { filtered.push(i); continue; }
            if ((g.white + ' ' + g.black + ' ' + g.event + ' ' + g.date)
                .toLowerCase().includes(needle)) {
                filtered.push(i);
            }
        }
        windowStart = 0;
        // Stats describe the current filter, so searching narrows them too.
        renderStats(filtered.map(function (i) { return games[i]; }));
        renderOptions();
        if (filtered.length) selectGame(0);
        else statusEl.textContent = 'No games match that search.';
    }

    async function load() {
        const response = await fetch(DATA_URL);
        if (!response.ok) throw new Error('HTTP ' + response.status);
        // The file is served as .gz; DecompressionStream avoids shipping a
        // gunzip implementation.
        const stream = response.body.pipeThrough(new DecompressionStream('gzip'));
        return await new Response(stream).text();
    }

    board = new Chessboard(document.getElementById('gameBoard'), {
        position: FEN.start,
        assetsUrl: "/vendor/cm-chessboard/assets/",
        style: {pieces: {file: "pieces/standard.svg"}}
    });

    load().then(function (pgn) {
        games = splitGames(pgn);
        if (!games.length) {
            playersEl.textContent = 'No games found in the archive.';
            return;
        }
        renderYears();
        applyFilter('');
    }).catch(function (error) {
        console.error('Could not load games:', error);
        playersEl.textContent = 'Could not load the game archive.';
    });

    searchEl.addEventListener('input', function () { applyFilter(searchEl.value); });
    yearEl.addEventListener('change', function () { applyFilter(searchEl.value); });
    selectEl.addEventListener('change', function () { selectGame(Number(selectEl.value)); });

    // Jump to an absolute position in the current filter. This is the only way
    // to reach a game beyond the <select>'s window, so it clamps rather than
    // rejects: typing 99999 lands on the last game instead of doing nothing.
    function jumpTo(value) {
        if (!filtered.length) return;
        const wanted = parseInt(value, 10);
        if (isNaN(wanted)) { jumpEl.value = String(currentGame + 1); return; }
        const clamped = Math.max(1, Math.min(wanted, filtered.length));
        selectGame(clamped - 1);
    }

    jumpEl.addEventListener('change', function () { jumpTo(jumpEl.value); });
    jumpEl.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') { event.preventDefault(); jumpTo(jumpEl.value); }
    });

    btnPrev.addEventListener('click', function () {
        if (currentMove > 0) { currentMove--; render(); }
    });
    btnNext.addEventListener('click', function () {
        if (currentMove < movesOf(games[filtered[currentGame]]).length) { currentMove++; render(); }
    });
    btnPrevGame.addEventListener('click', function () {
        if (currentGame > 0) selectGame(currentGame - 1);
    });
    btnNextGame.addEventListener('click', function () {
        // Bounded by the whole filtered list, not by MAX_OPTIONS: the <select>
        // is a sliding window now, so stepping past its end re-windows rather
        // than running out of games.
        if (currentGame < filtered.length - 1) selectGame(currentGame + 1);
    });

    // Arrow keys: left/right step moves, up/down step games. Ignored while the
    // search box has focus so typing still works.
    document.addEventListener('keydown', function (event) {
        // Also ignored in the year and jump controls: up/down are how a number
        // input and a <select> are meant to be operated, and stealing them
        // would make both unusable from the keyboard.
        const active = document.activeElement;
        if (active === searchEl || active === jumpEl || active === yearEl) return;
        const actions = {
            ArrowLeft: btnPrev, ArrowRight: btnNext,
            ArrowUp: btnPrevGame, ArrowDown: btnNextGame
        };
        const button = actions[event.key];
        if (button && !button.disabled) { event.preventDefault(); button.click(); }
    });
}());
</script>
