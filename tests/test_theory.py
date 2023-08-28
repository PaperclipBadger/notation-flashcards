import collections

import pytest

from notation_flashcards.theory import *



@pytest.fixture(params=Mode)
def mode(request) -> Mode:
    return request.param


def test_spelling(mode: Mode) -> None:
    # every scale should be spelled with every letter name once
    letters = set('ABCDEFG')
    for i in range(-8, 13):
        scale = KeySignature(circle(i), mode=mode)
        assert set(scale.name(n).letter for n in scale.scale) == letters


@pytest.mark.parametrize(
    ['root', 'num_sharps'],
    [(circle(i, mode=Mode.MAJOR), i) for i in range(8)],
)
def test_major_sharps(root: Note, num_sharps: int) -> None:
    scale = KeySignature(root, Mode.MAJOR)
    names = (scale.name(n) for n in scale.scale)

    counts = collections.Counter(name.accidental for name in names)

    assert counts[Accidental.SHARP] == num_sharps
    assert counts[Accidental.NONE] == 7 - num_sharps


@pytest.mark.parametrize(
    ['root', 'num_sharps'],
    [(circle(i, mode=Mode.MINOR), i) for i in range(8)],
)
def test_minor_sharps(root: Note, num_sharps: int) -> None:
    scale = KeySignature(root, Mode.MINOR)
    names = (scale.name(n) for n in scale.scale)

    counts = collections.Counter(name.accidental for name in names)

    assert counts[Accidental.SHARP] == num_sharps
    assert counts[Accidental.NONE] == 7 - num_sharps


@pytest.mark.parametrize(
    ['root', 'num_flats'],
    [(circle(-i, mode=Mode.MAJOR), i) for i in range(8)],
)
def test_major_sharps(root: Note, num_flats: int) -> None:
    scale = KeySignature(root, Mode.MAJOR)
    names = (scale.name(n) for n in scale.scale)

    counts = collections.Counter(name.accidental for name in names)

    assert counts[Accidental.FLAT] == num_flats
    assert counts[Accidental.NONE] == 7 - num_flats


@pytest.mark.parametrize(
    ['root', 'num_flats'],
    [(circle(-i, mode=Mode.MINOR), i) for i in range(8)],
)
def test_minor_flats(root: Note, num_flats: int) -> None:
    scale = KeySignature(root, Mode.MINOR)
    names = (scale.name(n) for n in scale.scale)

    counts = collections.Counter(name.accidental for name in names)

    assert counts[Accidental.FLAT] == num_flats
    assert counts[Accidental.NONE] == 7 - num_flats