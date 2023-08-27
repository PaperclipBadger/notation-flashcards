import typing

import dataclasses
import enum
import itertools


DIATONIC_SCALE = (0, 2, 4, 5, 7, 9, 11)
UNUSED = (1, 3, 6, 8, 10)


Note = typing.NewType('Note', int)


class Accidental(enum.Enum):
    NONE = 0
    FLAT = 'f'
    DOUBLEFLAT = 'bb'
    NATURAL = 'n'
    SHARP = 's'
    DOUBLESHARP = 'ss'

    @property
    def neoscore(self) -> str:
        return self.value

    @property
    def unicode(self) -> str:
        table = {
            Accidental.NONE: '',
            Accidental.DOUBLEFLAT: '𝄫',
            Accidental.FLAT: '♭',
            Accidental.NATURAL: '♮',
            Accidental.SHARP: '♯',
            Accidental.DOUBLESHARP: '𝄪',
        }
        return table[self]
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Accidental):
            if self.value == Accidental.NONE.value and other.value == Accidental.NATURAL.value:
                return True
            elif self.value == Accidental.NATURAL.value and other.value == Accidental.NONE.value:
                return True
            else:
                return self.value == other.value


class Mode(enum.IntEnum):
    IONIAN = 0
    DORIAN = 1
    PHRYGIAN = 2
    LYDIAN = 3
    MIXOLYDIAN = 4
    AEOLIAN = 5
    LOCRIAN = 6

    MAJOR = IONIAN
    MINOR = AEOLIAN


@dataclasses.dataclass(frozen=True)
class EngravingInfo:
    letter: str
    accidental: Accidental = Accidental.NONE
    octave: int = 0

    def __str__(self) -> str:
        return ''.join(
            (
                self.letter.lower(),
                self.accidental.neoscore,
                "'" * self.octave if self.octave >= 0 else "," * -self.octave,
            )
        )


@dataclasses.dataclass(frozen=True)
class NoteName:
    letter: str
    accidental: Accidental = Accidental.NONE

    @property
    def note(self) -> Note:
        letter_index = DIATONIC_SCALE['CDEFGAB'.index(self.letter.upper())]
        if self.accidental in (Accidental.NONE, Accidental.NATURAL):
            offset = 0
        elif self.accidental == Accidental.SHARP:
            offset = 1
        elif self.accidental == Accidental.DOUBLESHARP:
            offset = 2
        elif self.accidental == Accidental.FLAT:
            offset = -1
        elif self.accidental == Accidental.DOUBLEFLAT:
            offset = -2
        return Note((letter_index + offset) % 12)

    def __str__(self) -> str:
        return self.letter + self.accidental.unicode
    
    def __eq__(self, other) -> bool:
        if isinstance(other, NoteName):
            return self.note == other.note
        return NotImplemented


class ChromaticScale:
    root = 0
    notes = tuple(range(12))
    names = (
        NoteName('C'),
        NoteName('C', Accidental.SHARP),
        NoteName('D'),
        NoteName('D', Accidental.SHARP),
        NoteName('E'),
        NoteName('F'),
        NoteName('F', Accidental.SHARP),
        NoteName('G'),
        NoteName('G', Accidental.SHARP),
        NoteName('A'),
        NoteName('A', Accidental.SHARP),
        NoteName('B'),
    )

    @staticmethod
    def name(note: Note) -> NoteName:
        return ChromaticScale.names[note % 12]
    
    @staticmethod
    def engrave(note: Note) -> EngravingInfo:
        octave, index = divmod(note, 12)
        template = ChromaticScale.names[index]
        return EngravingInfo(
            letter=template.letter,
            accidental=template.accidental,
            octave=octave,
        )


class Scale:
    root: Note
    notes: typing.Sequence[Note]

    def name(self, note: Note) -> NoteName:
        ...
    
    def engrave(self, note: Note) -> EngravingInfo:
        ...
    

class KeySignature:
    root: Note
    notes: typing.Sequence[Note]

    def __init__(self, root: NoteName, mode: Mode) -> None:
        self.root = root.note

        diatonic_root = self.root - DIATONIC_SCALE[mode]
        self.notes = [
            (diatonic_root + offset) % 12
            for offset in rotate(mode, DIATONIC_SCALE)
        ]

        self.names = [None] * 12

        # every note in the scale should have a unique letter name
        letters = [
            chr(ord('A') + (ord(root.letter) - ord('A') + i) % 7)
            for i in range(7)
        ]

        for note, letter in zip(self.notes, letters):
            for accidental in Accidental:
                candidate = NoteName(letter, accidental)
                if candidate.note == note:
                    self.names[note] = candidate
                    break
            else:
                assert False, f"could not label note {note} with {letter}"

        unused = (i for i in range(12) if i not in self.notes)
        for offset in unused:
            # notes that aren't in the scale get their standard name
            self.names[offset] = ChromaticScale.name(offset)
        
        assert all(name is not None for name in self.names)
    
    def name(self, note: Note) -> NoteName:
        return self.names[note % 12]
    
    def engrave(self, note: Note) -> EngravingInfo:
        octave, index = divmod(note, 12)
        template = self.name(note)
        if note % 12 in self.notes:
            # if it's in the scale, we engrave without an accidental
            # the accidental is already in the key signature
            return EngravingInfo(
                letter=template.letter,
                accidental=Accidental.NONE,
                octave=octave,
            )
        elif template.accidental in (Accidental.NONE, Accidental.SHARP, Accidental.FLAT):
            # if it's not in the scale and has no accidental,
            # then its sharp/flat is a scale note (so engrave with a natural)

            # if it has an accidental and is not a scale note,
            # then its natural is a scale note (so engrave with accidental)
            return EngravingInfo(
                letter=template.letter,
                accidental=(
                    Accidental.NATURAL
                    if template.accidental == Accidental.NONE
                    else template.accidental
                ),
                octave=octave,
            )
        elif template.accidental == Accidental.NATURAL:
            assert False, "we should never use naturals in note names"
        else:
            assert False, "this line of code should never run!"



T = typing.TypeVar('T')

def rotate(n: int, seq: typing.Sequence[T]) -> typing.Generator[T, None, None]:
    for i in range(len(seq)):
        yield seq[(i + n) % len(seq)]

