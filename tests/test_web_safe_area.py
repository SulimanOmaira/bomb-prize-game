"""Deployment checks for the mobile-safe web build."""

import base64
import re
from pathlib import Path

from screens.names_screen import MOBILE_INPUT_Z_INDEX


ROOT = Path(__file__).resolve().parents[1]


def test_public_game_pages_are_safe_and_in_sync() -> None:
    root_html = (ROOT / "public" / "index.html").read_text(encoding="utf-8-sig")
    game_html = (ROOT / "public" / "game" / "index.html").read_text(
        encoding="utf-8-sig"
    )

    assert root_html == game_html
    assert root_html.count('name="viewport"') == 1
    assert "viewport-fit=cover" in root_html
    assert "100dvh" in root_html
    assert (
        "https://pygame-web.github.io/cdn/cp312/"
        "pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl"
    ) in root_html
    assert (
        '"runtime/0.9.3/packages/cp312/'
        'pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl"'
    ) not in root_html
    for inset in ("top", "right", "bottom", "left"):
        assert f"safe-area-inset-{inset}" in root_html
    assert 'canvas.style.inset = "0"' not in root_html
    assert 'canvas.style.height = "100vh"' not in root_html


def test_native_name_fields_are_layered_between_canvas_and_loader() -> None:
    html = (ROOT / "public" / "index.html").read_text(encoding="utf-8-sig")
    canvas_match = re.search(r'canvas\.style\.zIndex = "(\d+)"', html)
    loader_match = re.search(
        r"#bomb-prize-loader\s*\{.*?z-index:\s*(\d+)",
        html,
        flags=re.DOTALL,
    )

    assert canvas_match is not None
    assert loader_match is not None
    assert int(canvas_match.group(1)) < MOBILE_INPUT_Z_INDEX
    assert MOBILE_INPUT_Z_INDEX < int(loader_match.group(1))


def test_embedded_web_bundle_matches_published_apk() -> None:
    html = (ROOT / "public" / "game" / "index.html").read_text(
        encoding="utf-8-sig"
    )
    match = re.search(
        r'^BOMB_PRIZE_APK_BASE64 = "([A-Za-z0-9+/=]+)"$',
        html,
        flags=re.MULTILINE,
    )

    assert match is not None
    embedded_apk = base64.b64decode(match.group(1), validate=True)
    root_apk = (ROOT / "public" / "bomb_prize_game.apk").read_bytes()
    game_apk = (ROOT / "public" / "game" / "bomb_prize_game.apk").read_bytes()
    assert embedded_apk == root_apk == game_apk


def test_web_shell_uses_dynamic_viewport_safe_area() -> None:
    styles = (ROOT / "app" / "styles.css").read_text(encoding="utf-8")

    assert "height: 100dvh" in styles
    for inset in ("top", "right", "bottom", "left"):
        assert f"env(safe-area-inset-{inset})" in styles


def test_sdl_keyboard_events_are_scoped_to_the_canvas() -> None:
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    hint = 'os.environ["SDL_EMSCRIPTEN_KEYBOARD_ELEMENT"] = "#canvas"'

    assert hint in source
    assert source.index(hint) < source.index("import pygame")
