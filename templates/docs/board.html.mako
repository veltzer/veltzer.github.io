<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimal Chessboard Test</title>
    
    <!-- cm-chessboard library CSS from unpkg -->
    <link rel="stylesheet" href="https://unpkg.com/cm-chessboard@8.6.0/dist/cm-chessboard.css"/>
    
    <!-- cm-chessboard library JavaScript Bundle from unpkg -->
    <script src="https://unpkg.com/cm-chessboard@8.6.0/dist/cm-chessboard.js"></script>

    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #333;
            margin: 0;
        }
        #board-container {
            width: 80vw;
            max-width: 600px;
        }
    </style>
</head>
<body>

    <div id="board-container"></div>

    <script>
        // Use window.onload to ensure the library script is fully loaded before we try to use it.
        window.onload = function() {
            // Configuration for the chessboard
            const config = {
                position: "start", // The starting position of the pieces
                sprite: {
                    url: "https://unpkg.com/cm-chessboard@8.6.0/assets/images/chessboard-sprite.svg",
                    size: 40,
                    cache: true
                }
            };

            // Create a new chessboard instance in the 'board-container' div
            new Chessboard(document.getElementById('board-container'), config);
        };
    </script>

</body>
</html>
