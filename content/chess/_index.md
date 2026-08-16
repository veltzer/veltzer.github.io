+++
title = "Chess Viewer"
template = "chess.html"
+++

<script src="/vendor/chess.min.js"></script>

<div class="chess-viewer">
  <p id="gamePlayers" class="chess-players">&nbsp;</p>
  <p id="gameCounter" class="chess-counter">&nbsp;</p>

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
    // cm-chessboard 8.x is ESM-only with relative imports, so this has to be
    // a module. Modules are deferred, so DOM is ready without window.onload.
    import {Chessboard, FEN} from "/vendor/cm-chessboard/src/Chessboard.js";

    (function() {
        // --- The games ---
        // Each entry is a PGN string. chess.js is strict about two things that
        // are easy to get wrong here: the header block and the movetext must be
        // separated by a blank line, and header lines must not start with
        // whitespace. Both are handled by cleanPgn() below, so these literals
        // can stay indented to match the surrounding code.
        const PGNS = [`
            [Event "A Night at the Opera"]
            [Site "Paris, France"]
            [Date "1858.11.02"]
            [Result "1-0"]
            [White "Paul Morphy"]
            [Black "Duke Karl / Count Isouard"]

            1.e4 e5 2.Nf3 d6 3.d4 Bg4 4.dxe5 Bxf3 5.Qxf3 dxe5 6.Bc4 Nf6 7.Qb3 Qe7
            8.Nc3 c6 9.Bg5 b5 10.Nxb5 cxb5 11.Bxb5+ Nbd7 12.O-O-O Rd8
            13.Rxd7 Rxd7 14.Rd1 Qe6 15.Bxd7+ Nxd7 16.Qb8+ Nxb8 17.Rd8# 1-0
        `, `
            [Event "The Immortal Game"]
            [Site "London, England"]
            [Date "1851.06.21"]
            [Result "1-0"]
            [White "Adolf Anderssen"]
            [Black "Lionel Kieseritzky"]

            1.e4 e5 2.f4 exf4 3.Bc4 Qh4+ 4.Kf1 b5 5.Bxb5 Nf6 6.Nf3 Qh6 7.d3 Nh5
            8.Nh4 Qg5 9.Nf5 c6 10.g4 Nf6 11.Rg1 cxb5 12.h4 Qg6 13.h5 Qg5 14.Qf3 Ng8
            15.Bxf4 Qf6 16.Nc3 Bc5 17.Nd5 Qxb2 18.Bd6 Bxg1 19.e5 Qxa1+ 20.Ke2 Na6
            21.Nxg7+ Kd8 22.Qf6+ Nxf6 23.Be7# 1-0
        `];

        // --- DOM references ---
        const statusEl = document.getElementById('status');
        const titleEl = document.getElementById('gameTitle');
        const playersEl = document.getElementById('gamePlayers');
        const counterEl = document.getElementById('gameCounter');
        const btnPrev = document.getElementById('btnPrev');
        const btnNext = document.getElementById('btnNext');
        const btnPrevGame = document.getElementById('btnPrevGame');
        const btnNextGame = document.getElementById('btnNextGame');

        // --- State ---
        let board = null;
        let games = [];        // [{event, white, black, moves}]
        let currentGame = 0;
        let currentMove = 0;

        function cleanPgn(pgn) {
            return pgn.split('\n').map(function(line) {
                return line.trim();
            }).join('\n').trim();
        }

        // Parse every PGN up front so a bad one is caught before rendering.
        function loadGames() {
            const loaded = [];
            for (let i = 0; i < PGNS.length; i++) {
                const chess = new Chess();
                if (!chess.load_pgn(cleanPgn(PGNS[i]))) {
                    return null;
                }
                const headers = chess.header();
                loaded.push({
                    event: headers.Event || 'Game ' + (i + 1),
                    white: headers.White || 'White',
                    black: headers.Black || 'Black',
                    date: headers.Date || '',
                    moves: chess.history({verbose: true})
                });
            }
            return loaded;
        }

        function render() {
            const game = games[currentGame];
            const move = game.moves[currentMove - 1];

            const year = game.date ? game.date.slice(0, 4) : '';
            titleEl.textContent = game.event + (year ? ' (' + year + ')' : '');
            playersEl.textContent = game.white + ' vs. ' + game.black;
            counterEl.textContent = 'Game ' + (currentGame + 1) + ' of ' + games.length;
            statusEl.textContent = 'Move ' + currentMove + ': ' +
                (move ? move.san : 'Start');

            // Replay from the start rather than tracking incremental state --
            // the games are short and this cannot drift out of sync.
            const position = new Chess();
            game.moves.slice(0, currentMove).forEach(function(m) {
                position.move(m.san);
            });
            board.setPosition(position.fen(), true);

            btnPrev.disabled = currentMove === 0;
            btnNext.disabled = currentMove === game.moves.length;
            btnPrevGame.disabled = currentGame === 0;
            btnNextGame.disabled = currentGame === games.length - 1;
        }

        function selectGame(index) {
            currentGame = index;
            currentMove = 0;   // always open a game at its starting position
            render();
        }

        // --- Init ---
        games = loadGames();
        if (!games || games.length === 0) {
            statusEl.textContent = 'Could not load the games.';
            return;
        }

        // 8.x replaced the old `sprite: {url, size}` option with assetsUrl plus
        // a pieces file relative to it, and `position: "start"` must be FEN.start.
        board = new Chessboard(document.getElementById('gameBoard'), {
            position: FEN.start,
            assetsUrl: "/vendor/cm-chessboard/assets/",
            style: {pieces: {file: "pieces/standard.svg"}}
        });

        btnPrev.addEventListener('click', function() {
            if (currentMove > 0) {
                currentMove--;
                render();
            }
        });

        btnNext.addEventListener('click', function() {
            if (currentMove < games[currentGame].moves.length) {
                currentMove++;
                render();
            }
        });

        btnPrevGame.addEventListener('click', function() {
            if (currentGame > 0) {
                selectGame(currentGame - 1);
            }
        });

        btnNextGame.addEventListener('click', function() {
            if (currentGame < games.length - 1) {
                selectGame(currentGame + 1);
            }
        });

        // Arrow keys: left/right step moves, up/down step games.
        document.addEventListener('keydown', function(event) {
            const actions = {
                ArrowLeft: btnPrev,
                ArrowRight: btnNext,
                ArrowUp: btnPrevGame,
                ArrowDown: btnNextGame
            };
            const button = actions[event.key];
            if (button && !button.disabled) {
                event.preventDefault();
                button.click();
            }
        });

        render();
    }());
</script>
