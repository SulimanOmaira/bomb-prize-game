"""Tests for browser viewport and responsive game sizing."""

from game.settings import choose_content_size, choose_display_size


def test_portrait_phone_uses_compact_content() -> None:
    assert choose_content_size((390, 844)) == (480, 700)


def test_desktop_keeps_original_content_size() -> None:
    assert choose_content_size((1440, 900)) == (900, 700)


def test_portrait_display_matches_browser_aspect_ratio() -> None:
    width, height = choose_display_size((480, 700), (390, 844))

    assert width == 480
    assert height == 1039


def test_landscape_display_matches_browser_aspect_ratio() -> None:
    width, height = choose_display_size((900, 700), (844, 390))

    assert width == 1515
    assert height == 700
