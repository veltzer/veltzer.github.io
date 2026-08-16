+++
title = "Chessboard"
template = "chess.html"
+++

<div class="chess-viewer">
  <p class="chess-players">A plain board in the starting position.</p>
  <div id="board-container" class="chess-board"></div>
</div>

<script type="module">
// cm-chessboard 8.x is ESM-only with relative imports, so this has to be a
// module. Modules are deferred, so the DOM is ready without window.onload.
import {Chessboard, FEN} from "/vendor/cm-chessboard/src/Chessboard.js";

new Chessboard(document.getElementById('board-container'), {
    // 8.x wants a FEN string; the old "start" shorthand throws inside
    // Position.setFen. The sprite option was likewise replaced by assetsUrl
    // plus a pieces file relative to it.
    position: FEN.start,
    assetsUrl: "/vendor/cm-chessboard/assets/",
    style: {pieces: {file: "pieces/standard.svg"}}
});
</script>
