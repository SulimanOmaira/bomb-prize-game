"""Tests for the native name fields used by mobile web browsers."""

import platform
import sys
from types import SimpleNamespace

from game.settings import MAX_NAME_LENGTH
from screens.names_screen import (
    MOBILE_INPUT_IDS,
    MOBILE_INPUT_Z_INDEX,
    NamesScreen,
)


class FakeElement:
    def __init__(self, document: "FakeDocument", tag_name: str) -> None:
        self.document = document
        self.tagName = tag_name.upper()
        self.id = ""
        self.type = ""
        self.value = ""
        self.style = SimpleNamespace()
        self.attributes: dict[str, str] = {}
        self.focus_count = 0
        self.blur_count = 0

    def setAttribute(self, name: str, value: str) -> None:
        self.attributes[name] = value

    def focus(self) -> None:
        self.focus_count += 1
        self.document.activeElement = self

    def blur(self) -> None:
        self.blur_count += 1
        if self.document.activeElement is self:
            self.document.activeElement = None

    def getBoundingClientRect(self) -> SimpleNamespace:
        return SimpleNamespace(left=0, top=0, width=900, height=700)


class FakeBody:
    def __init__(self, document: "FakeDocument") -> None:
        self.document = document

    def appendChild(self, element: FakeElement) -> None:
        self.document.elements[element.id] = element


class FakeDocument:
    def __init__(self) -> None:
        self.elements: dict[str, FakeElement] = {}
        self.activeElement: FakeElement | None = None
        self.body = FakeBody(self)
        canvas = FakeElement(self, "canvas")
        canvas.id = "canvas"
        self.elements[canvas.id] = canvas

    def createElement(self, tag_name: str) -> FakeElement:
        return FakeElement(self, tag_name)

    def getElementById(self, element_id: str) -> FakeElement | None:
        return self.elements.get(element_id)


def use_fake_browser(monkeypatch) -> FakeDocument:
    document = FakeDocument()
    monkeypatch.setattr(sys, "platform", "emscripten")
    monkeypatch.setattr(platform, "document", document, raising=False)
    return document


def test_mobile_fields_exist_above_canvas_before_the_first_tap(monkeypatch) -> None:
    document = use_fake_browser(monkeypatch)
    screen = NamesScreen()

    screen._show_mobile_inputs()

    assert screen.mobile_inputs_visible
    for element_id in MOBILE_INPUT_IDS:
        element = document.getElementById(element_id)
        assert element is not None
        assert element.tagName == "INPUT"
        assert element.type == "text"
        assert element.maxLength == MAX_NAME_LENGTH
        assert element.style.display == "block"
        assert int(element.style.zIndex) == MOBILE_INPUT_Z_INDEX
        assert element.style.pointerEvents == "auto"
        assert element.focus_count == 0
        for event_name in ("keydown", "keypress", "keyup"):
            assert (
                element.attributes[f"on{event_name}"]
                == "event.stopPropagation()"
            )


def test_mobile_fields_sync_both_names_and_the_focused_player(monkeypatch) -> None:
    document = use_fake_browser(monkeypatch)
    screen = NamesScreen()
    screen._show_mobile_inputs()
    first = document.getElementById(MOBILE_INPUT_IDS[0])
    second = document.getElementById(MOBILE_INPUT_IDS[1])
    assert first is not None and second is not None

    first.value = "Alice"
    second.value = "B" * (MAX_NAME_LENGTH + 5)
    document.activeElement = second
    screen._sync_mobile_input()

    assert screen.names == ["Alice", "B" * MAX_NAME_LENGTH]
    assert screen.active_index == 1
    assert screen.mobile_input_index == 1


def test_hiding_mobile_fields_removes_both_overlays(monkeypatch) -> None:
    document = use_fake_browser(monkeypatch)
    screen = NamesScreen()
    screen._show_mobile_inputs()
    first = document.getElementById(MOBILE_INPUT_IDS[0])
    second = document.getElementById(MOBILE_INPUT_IDS[1])
    assert first is not None and second is not None
    document.activeElement = first

    screen.hide_mobile_input()

    assert first.style.display == "none"
    assert second.style.display == "none"
    assert first.blur_count == 1
    assert second.blur_count == 1
    assert document.activeElement is None
    assert screen.mobile_input_index is None
    assert not screen.mobile_inputs_visible
