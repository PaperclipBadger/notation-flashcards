import collections

import pytest

from notation_flashcards.theory import *



@pytest.fixture(params=Mode)
def mode(request) -> Mode:
    return request.param


# circle of fifths!
CIRCLE_OF_FIFTHS = 'FCGDAEB'

def get_keysig_root(i: int, mode: Mode) -> NoteName:
    if mode == Mode.MAJOR:
        offset = 1
    elif mode == Mode.MINOR:
        offset = 4

    rank, position = divmod(i + offset, 7)
    letter = CIRCLE_OF_FIFTHS[position]

    if rank == -1:
        accidental = Accidental.FLAT
    elif rank == 0:
        accidental = Accidental.NONE
    elif rank == 1:
        accidental = Accidental.SHARP
    
    return NoteName(letter, accidental)


def test_spelling(mode: Mode) -> None:
    # every scale should be spelled with every letter name once
    letters = set('ABCDEFG')
    for i in range(-7, 12):
        scale = KeySignature(get_keysig_root(i, mode=Mode.MAJOR), mode=mode)
        assert set(scale.name(n).letter for n in scale.notes) == letters


@pytest.mark.parametrize(
    ['root', 'num_sharps'],
    [(get_keysig_root(i, mode=Mode.MAJOR), i) for i in range(8)],
)
def test_major_sharps(root: Note, num_sharps: int) -> None:
    scale = KeySignature(root, Mode.MAJOR)
    names = (scale.name(n) for n in scale.notes)

    counts = collections.Counter(name.accidental for name in names)

    assert counts[Accidental.SHARP] == num_sharps
    assert counts[Accidental.NONE] == 7 - num_sharps


@pytest.mark.parametrize(
    ['root', 'num_sharps'],
    [(get_keysig_root(i, mode=Mode.MINOR), i) for i in range(8)],
)
def test_minor_sharps(root: Note, num_sharps: int) -> None:
    scale = KeySignature(root, Mode.MINOR)
    names = (scale.name(n) for n in scale.notes)

    counts = collections.Counter(name.accidental for name in names)

    assert counts[Accidental.SHARP] == num_sharps
    assert counts[Accidental.NONE] == 7 - num_sharps


@pytest.mark.parametrize(
    ['root', 'num_flats'],
    [(get_keysig_root(-i, mode=Mode.MAJOR), i) for i in range(8)],
)
def test_major_sharps(root: Note, num_flats: int) -> None:
    scale = KeySignature(root, Mode.MAJOR)
    names = (scale.name(n) for n in scale.notes)

    counts = collections.Counter(name.accidental for name in names)

    assert counts[Accidental.FLAT] == num_flats
    assert counts[Accidental.NONE] == 7 - num_flats


@pytest.mark.parametrize(
    ['root', 'num_flats'],
    [(get_keysig_root(-i, mode=Mode.MINOR), i) for i in range(8)],
)
def test_minor_flats(root: Note, num_flats: int) -> None:
    scale = KeySignature(root, Mode.MINOR)
    names = (scale.name(n) for n in scale.notes)

    counts = collections.Counter(name.accidental for name in names)

    assert counts[Accidental.FLAT] == num_flats
    assert counts[Accidental.NONE] == 7 - num_flats