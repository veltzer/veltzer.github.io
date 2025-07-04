<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Chess Game Viewer</title>
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/favicon.svg">
    
    <!-- Tailwind CSS for styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- chessboard.js CSS -->
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css" xintegrity="sha384-q94+BZGI/DcVSkQu3UdtoShftBqwBCDFsAWYoOA2V0ciTFlKXekJ/5+XpfZqrPrN" crossorigin="anonymous">
    
    <!-- jQuery is a dependency for chessboard.js -->
    <script src="https://code.jquery.com/jquery-3.5.1.min.js" xintegrity="sha384-ZvpUoO/+PpLXR1lu4jmpXWu80pZlYUAfxl5NsBMWOEPSjUn/6Z/hRTt8+pR6L4N2" crossorigin="anonymous"></script>
    
    <!-- chess.js for game logic (browser-compatible version) -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
    
    <!-- chessboard.js library -->
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js" xintegrity="sha384-8Vi8VHwn3vjQ9eUHUxex3JSN/NFqUg3iGDIPd44a5WLgCFsengh+rrV6RGIadDRL" crossorigin="anonymous"></script>

    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .nav-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
</head>
<body class="bg-gray-800 text-white flex items-center justify-center min-h-screen">

    <div class="text-center p-4">
        <h1 class="text-3xl font-bold mb-4">Opera Game (1858)</h1>
        <p class="mb-4 text-gray-400">Paul Morphy vs. Duke Karl / Count Isouard</p>
        
        <!-- The chessboard will be rendered here -->
        <div id="gameBoard" class="w-full max-w-lg mx-auto mb-4"></div>
        
        <!-- Navigation controls -->
        <div class="space-x-4">
            <button id="btnPrev" class="nav-btn bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg">Previous</button>
            <button id="btnNext" class="nav-btn bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg">Next</button>
        </div>
        
        <!-- Display the current move -->
        <div id="status" class="mt-4 text-lg font-mono"></div>
    </div>

    <script>
        window.onload = function () {
            // --- Global State Variables ---
            let board = null;
            const game = new Chess();
            let moveHistory = [];
            let currentMove = 0;

            // --- Hardcoded PGN for the Opera Game ---
            const pgn = `
                [Event "A Night at the Opera"]
                [Site "Paris, France"]
                [Date "1858.11.02"]
                [EventDate "?"]
                [Round "?"]
                [Result "1-0"]
                [White "Paul Morphy"]
                [Black "Duke Karl / Count Isouard"]
                [ECO "C41"]
                [WhiteElo "?"]
                [BlackElo "?"]
                [PlyCount "33"]

                1.e4 e5 2.Nf3 d6 3.d4 Bg4 4.dxe5 Bxf3 5.Qxf3 dxe5 6.Bc4 Nf6 7.Qb3 Qe7
                8.Nc3 c6 9.Bg5 b5 10.Nxb5 cxb5 11.Bxb5+ Nbd7 12.O-O-O Rd8
                13.Rxd7 Rxd7 14.Rd1 Qe6 15.Bxd7+ Nxd7 16.Qb8+ Nxb8 17.Rd8# 1-0
            `;

            // --- DOM Element References ---
            const statusEl = document.getElementById('status');
            const btnPrev = document.getElementById('btnPrev');
            const btnNext = document.getElementById('btnNext');

            // --- Function to update the board and UI ---
            function updateStatus() {
                const move = moveHistory[currentMove - 1] || { san: 'Start' };
                // Mako-safe string concatenation
                statusEl.textContent = 'Move ' + currentMove + ': ' + move.san;
                
                // Set board to the current position
                const tempGame = new Chess();
                moveHistory.slice(0, currentMove).forEach(m => tempGame.move(m.san));
                board.position(tempGame.fen());

                // Update button states
                btnPrev.disabled = currentMove === 0;
                btnNext.disabled = currentMove === moveHistory.length;
            }

            // --- Initialize the Game ---
            game.load_pgn(pgn);
            moveHistory = game.history({ verbose: true });

            // --- Initialize the Board ---
            const boardConfig = {
                draggable: false,
                position: 'start'
            };
            board = Chessboard('gameBoard', boardConfig);

            // --- Event Listeners ---
            btnPrev.addEventListener('click', () => {
                if (currentMove > 0) {
                    currentMove--;
                    updateStatus();
                }
            });

            btnNext.addEventListener('click', () => {
                if (currentMove < moveHistory.length) {
                    currentMove++;
                    updateStatus();
                }
            });

            // --- Initial Render ---
            updateStatus();
        };
    </script>

</body>
</html>
