export default function GamePage() {
  return (
    <main className="game-shell">
      <iframe
        className="game-frame"
        src="/game/index.html?v=6"
        title="Bomb Prize Game"
        allow="autoplay; fullscreen"
      />
    </main>
  );
}
