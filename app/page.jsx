export default function GamePage() {
  return (
    <main className="game-shell">
      <iframe
        className="game-frame"
        src="/game/index.html"
        title="Bomb Prize Game"
        allow="autoplay; fullscreen"
      />
    </main>
  );
}
