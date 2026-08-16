+++
title = "Chess Viewer"
template = "chess.html"
+++

<script src="/vendor/chess.min.js"></script>

<div class="chess-viewer">
  <p id="gamePlayers" class="chess-players">Loading games…</p>
  <p id="gameCounter" class="chess-counter">&nbsp;</p>

  <div class="chess-picker">
    <label class="visually-hidden" for="gameSearch">Search games</label>
    <input type="search" id="gameSearch" class="chess-search"
           placeholder="Search by player, event or year…" autocomplete="off">
    <label class="visually-hidden" for="gameSelect">Game</label>
    <select id="gameSelect" class="chess-select"></select>
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

    const titleEl = document.getElementById('gameTitle');
    const playersEl = document.getElementById('gamePlayers');
    const counterEl = document.getElementById('gameCounter');
    const statusEl = document.getElementById('status');
    const searchEl = document.getElementById('gameSearch');
    const selectEl = document.getElementById('gameSelect');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const btnPrevGame = document.getElementById('btnPrevGame');
    const btnNextGame = document.getElementById('btnNextGame');

    let board = null;
    let games = [];        // {white, black, event, date, year, text, moves|null}
    let filtered = [];     // indices into games
    let currentGame = 0;   // index into filtered
    let currentMove = 0;

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
                date: date,
                year: (date.match(/^(\d{4})/) || [])[1] || '',
                text: text,
                moves: null
            });
        }
        return out;
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
        const clean = game.text.split('\n').map(function (line) {
            return line.trim();
        }).join('\n');
        game.moves = chess.load_pgn(clean) ? chess.history({verbose: true}) : [];
        return game.moves;
    }

    function renderOptions() {
        const shown = filtered.slice(0, MAX_OPTIONS);
        selectEl.innerHTML = shown.map(function (gameIndex, position) {
            return '<option value="' + position + '">' +
                   label(games[gameIndex], gameIndex) + '</option>';
        }).join('');
        const hidden = filtered.length - shown.length;
        counterEl.textContent = filtered.length.toLocaleString() + ' games' +
            (hidden > 0 ? ' (showing the first ' + MAX_OPTIONS.toLocaleString() + ')' : '');
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
        btnNextGame.disabled = currentGame >= Math.min(filtered.length, MAX_OPTIONS) - 1;
    }

    function selectGame(index) {
        currentGame = index;
        currentMove = 0;      // always open a game at its starting position
        render();
    }

    function applyFilter(query) {
        const needle = query.trim().toLowerCase();
        filtered = [];
        for (let i = 0; i < games.length; i++) {
            if (!needle) { filtered.push(i); continue; }
            const g = games[i];
            if ((g.white + ' ' + g.black + ' ' + g.event + ' ' + g.date)
                .toLowerCase().includes(needle)) {
                filtered.push(i);
            }
        }
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
        applyFilter('');
    }).catch(function (error) {
        console.error('Could not load games:', error);
        playersEl.textContent = 'Could not load the game archive.';
    });

    searchEl.addEventListener('input', function () { applyFilter(searchEl.value); });
    selectEl.addEventListener('change', function () { selectGame(Number(selectEl.value)); });

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
        if (currentGame < Math.min(filtered.length, MAX_OPTIONS) - 1) selectGame(currentGame + 1);
    });

    // Arrow keys: left/right step moves, up/down step games. Ignored while the
    // search box has focus so typing still works.
    document.addEventListener('keydown', function (event) {
        if (document.activeElement === searchEl) return;
        const actions = {
            ArrowLeft: btnPrev, ArrowRight: btnNext,
            ArrowUp: btnPrevGame, ArrowDown: btnNextGame
        };
        const button = actions[event.key];
        if (button && !button.disabled) { event.preventDefault(); button.click(); }
    });
}());
</script>
