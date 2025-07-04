<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PGN Chess Viewer</title>
    
    <!-- Tailwind CSS for styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- cm-chessboard library (CSS) -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/cm-chessboard@7/styles/cm-chessboard.css"/>
    
    <!-- chess.js for game logic and PGN parsing -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.2/chess.min.js"></script>
    
    <!-- cm-chessboard library (JavaScript Bundle) -->
    <script src="https://cdn.jsdelivr.net/npm/cm-chessboard@7/dist/cm-chessboard.bundle.js"></script>

    <style>
        /* Custom styles for a better look and feel */
        body {
            font-family: 'Inter', sans-serif;
        }
        .move-list {
            height: 400px; /* Adjust height as needed */
        }
        .move-list span.current-move {
            background-color: #4a5568; /* bg-gray-700 */
            color: white;
            border-radius: 4px;
            padding: 2px 4px;
        }
        .nav-btn {
            transition: all 0.2s ease-in-out;
        }
        .nav-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .nav-btn:hover:not(:disabled) {
            transform: translateY(-2px);
        }
        /* Ensure the board is responsive */
        #gameBoard {
            width: 100%;
            max-width: 600px; /* Set a max-width for larger screens */
            margin: 0 auto;
        }
    </style>
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
</head>
<body class="bg-gray-900 text-white flex items-center justify-center min-h-screen p-4">

    <div class="w-full max-w-6xl mx-auto">
        <header class="text-center mb-6">
            <h1 class="text-4xl font-bold">PGN Chess Game Viewer</h1>
            <p class="text-gray-400 mt-2">Browse the collection of chess games below.</p>
        </header>

        <main class="bg-gray-800 p-4 sm:p-8 rounded-2xl shadow-2xl grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <!-- Left Column: Controls and Game List -->
            <div class="lg:col-span-1 flex flex-col space-y-6">
                <div>
                    <label for="gameSelect" class="block mb-2 text-sm font-medium text-gray-300">Select a Game</label>
                    <select id="gameSelect" class="w-full bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 p-2.5" disabled>
                        <option>Loading games...</option>
                    </select>
                </div>

                <div id="gameInfo" class="bg-gray-700 p-4 rounded-lg text-sm space-y-2 hidden">
                    <p><strong>White:</strong> <span id="whitePlayer"></span></p>
                    <p><strong>Black:</strong> <span id="blackPlayer"></span></p>
                    <p><strong>Result:</strong> <span id="gameResult"></span></p>
                </div>

                <div id="moveHistory" class="bg-gray-900 p-4 rounded-lg overflow-y-auto move-list hidden">
                    <!-- Move history will be populated here -->
                </div>
            </div>

            <!-- Middle Column: Chess Board and Navigation -->
            <div class="lg:col-span-2 flex flex-col items-center justify-center">
                <div id="gameBoard" class="w-full mb-4"></div>
                
                <div id="navigation" class="flex items-center space-x-2 sm:space-x-4 bg-gray-700 p-3 rounded-xl shadow-lg hidden">
                    <button id="btnStart" class="nav-btn bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" /></svg>
                    </button>
                    <button id="btnPrev" class="nav-btn bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
                    </button>
                    <span id="moveCounter" class="text-lg font-mono w-24 text-center">0 / 0</span>
                    <button id="btnNext" class="nav-btn bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                    </button>
                    <button id="btnEnd" class="nav-btn bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" /></svg>
                    </button>
                </div>
            </div>

        </main>
    </div>

    <script>
        // Use window.onload to ensure all external scripts are loaded before our code runs
        window.onload = function () {
            // --- Global State Variables ---
            let board = null;
            const chess = new Chess();
            let games = [];
            let gameHistory = [];
            let currentMove = -1;

            // --- DOM Element References ---
            const gameSelect = document.getElementById('gameSelect');
            const gameInfoDiv = document.getElementById('gameInfo');
            const moveHistoryDiv = document.getElementById('moveHistory');
            const navigationDiv = document.getElementById('navigation');
            const boardDiv = document.getElementById('gameBoard');
            
            const whitePlayerSpan = document.getElementById('whitePlayer');
            const blackPlayerSpan = document.getElementById('blackPlayer');
            const gameResultSpan = document.getElementById('gameResult');
            const moveCounterSpan = document.getElementById('moveCounter');

            const btnStart = document.getElementById('btnStart');
            const btnPrev = document.getElementById('btnPrev');
            const btnNext = document.getElementById('btnNext');
            const btnEnd = document.getElementById('btnEnd');

            // --- Chessboard Configuration ---
            const boardConfig = {
                position: "start",
                sprite: {
                    url: "https://cdn.jsdelivr.net/npm/cm-chessboard@7/assets/images/chessboard-sprite.svg",
                    size: 40,
                    cache: true
                }
            };
            // Use the global CM object provided by the bundled script
            board = new CM.Chessboard(boardDiv, boardConfig);

            // --- Event Listeners ---
            gameSelect.addEventListener('change', loadSelectedGame, false);
            btnStart.addEventListener('click', () => updateToMove(-1));
            btnPrev.addEventListener('click', () => updateToMove(currentMove - 1));
            btnNext.addEventListener('click', () => updateToMove(currentMove + 1));
            btnEnd.addEventListener('click', () => updateToMove(gameHistory.length - 1));

            /**
             * Fetches the PGN file from a URL and processes it.
             * @param {string} url The URL of the PGN file.
             */
            async function loadPgnFromUrl(url) {
                try {
                    const response = await fetch(url);
                    if (!response.ok) {
                        throw new Error('HTTP error! status: ' + response.status);
                    }
                    const pgnData = await response.text();
                    
                    // Split the PGN data into individual games.
                    games = pgnData.split('\n[Event "').map((g, i) => i > 0 ? '[Event "' + g : g).filter(g => g.trim() !== "");
                    
                    if (games.length > 0) {
                        populateGameSelect();
                        loadSelectedGame(); // Load the first game by default
                    } else {
                        gameSelect.innerHTML = '<option>No games found in file.</option>';
                        console.error("No games found in the PGN file.");
                    }
                } catch (error) {
                    console.error('Could not fetch PGN file:', error);
                    gameSelect.innerHTML = '<option>Error loading games.</option>';
                }
            }

            /**
             * Populates the game selection dropdown with games found in the PGN.
             */
            function populateGameSelect() {
                gameSelect.innerHTML = '';
                games.forEach((pgn, index) => {
                    const tempChess = new Chess();
                    tempChess.load_pgn(pgn);
                    const headers = tempChess.header();
                    const white = headers.White || 'Unknown';
                    const black = headers.Black || 'Unknown';
                    const option = document.createElement('option');
                    option.value = index;
                    option.textContent = white + ' vs ' + black;
                    gameSelect.appendChild(option);
                });
                gameSelect.disabled = false;
            }

            /**
             * Loads the game selected from the dropdown into the chess engine.
             */
            function loadSelectedGame() {
                const selectedIndex = gameSelect.value;
                if (selectedIndex < 0 || selectedIndex >= games.length) return;

                const pgn = games[selectedIndex];
                const loadSuccessful = chess.load_pgn(pgn);

                if (loadSuccessful) {
                    gameHistory = chess.history({ verbose: true });
                    const headers = chess.header();
                    
                    // Display game info
                    whitePlayerSpan.textContent = headers.White || 'N/A';
                    blackPlayerSpan.textContent = headers.Black || 'N/A';
                    gameResultSpan.textContent = headers.Result || 'N/A';
                    gameInfoDiv.classList.remove('hidden');
                    navigationDiv.classList.remove('hidden');
                    moveHistoryDiv.classList.remove('hidden');

                    populateMoveHistory();
                    updateToMove(-1); // Go to the starting position
                } else {
                    console.error("Error loading the selected game PGN.");
                }
            }

            /**
             * Creates and displays the full list of moves for the current game.
             */
            function populateMoveHistory() {
                moveHistoryDiv.innerHTML = '';
                let moveNumber = 1;
                for (let i = 0; i < gameHistory.length; i += 2) {
                    const whiteMove = gameHistory[i];
                    const blackMove = gameHistory[i + 1];
                    
                    const movePair = document.createElement('div');
                    movePair.className = 'move-pair mb-1';
                    
                    let html = '<span class="text-gray-500 mr-2">' + moveNumber + '.</span>';
                    html += '<span class="font-semibold cursor-pointer" data-move-index="' + i + '">' + whiteMove.san + '</span>';
                    
                    if (blackMove) {
                        html += ' <span class="font-semibold cursor-pointer ml-2" data-move-index="' + (i + 1) + '">' + blackMove.san + '</span>';
                    }
                    
                    movePair.innerHTML = html;
                    moveHistoryDiv.appendChild(movePair);
                    moveNumber++;
                }

                // Add click listeners to moves
                moveHistoryDiv.querySelectorAll('[data-move-index]').forEach(span => {
                    span.addEventListener('click', (e) => {
                        const moveIndex = parseInt(e.target.getAttribute('data-move-index'));
                        updateToMove(moveIndex);
                    });
                });
            }

            /**
             * Updates the board and UI to a specific move index.
             * @param {number} moveIndex The index in the gameHistory array. -1 for start.
             */
            function updateToMove(moveIndex) {
                if (moveIndex < -1 || moveIndex >= gameHistory.length) return;

                currentMove = moveIndex;

                // To get the FEN at a specific move, we replay the game from the start.
                const tempChess = new Chess();
                // FIXED: The for loop was missing i++ causing an infinite loop.
                for (let i = 0; i <= currentMove; i++) {
                    tempChess.move(gameHistory[i].san);
                }
                
                board.setPosition(tempChess.fen());
                updateUI();
            }

            /**
             * Updates all UI elements based on the current move state.
             */
            function updateUI() {
                // Update move counter
                moveCounterSpan.textContent = (currentMove + 1) + ' / ' + gameHistory.length;

                // Update navigation button states
                btnStart.disabled = currentMove <= -1;
                btnPrev.disabled = currentMove <= -1;
                btnNext.disabled = currentMove >= gameHistory.length - 1;
                btnEnd.disabled = currentMove >= gameHistory.length - 1;

                // Highlight current move in the list
                moveHistoryDiv.querySelectorAll('.current-move').forEach(el => el.classList.remove('current-move'));
                if (currentMove > -1) {
                    const currentMoveEl = moveHistoryDiv.querySelector('[data-move-index="' + currentMove + '"]');
                    if (currentMoveEl) {
                        currentMoveEl.classList.add('current-move');
                        // Scroll to the highlighted move
                        currentMoveEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                }
            }

            // --- Initial Load ---
            loadPgnFromUrl('data/games.pgn');
        };
    </script>

</body>
</html>
