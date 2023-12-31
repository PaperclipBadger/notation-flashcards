import typing

import dataclasses
import enum


DIATONIC_SCALE = (0, 2, 4, 5, 7, 9, 11)
UNUSED = (1, 3, 6, 8, 10)


Note = typing.NewType('Note', int)


class Accidental(enum.Enum):
    NONE = 0
    DOUBLEFLAT = 1
    FLAT = 2
    NATURAL = 3
    SHARP = 4
    DOUBLESHARP = 5

    @property
    def neoscore(self) -> str:
        table = ('', 'ff', 'f', 'n', 's', 'ss')
        return table[self.value]

    @property
    def unicode(self) -> str:
        table = ('', '𝄫', '♭', '♮', '♯', '𝄪')
        return table[self.value]
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Accidental):
            if self.value == Accidental.NONE.value and other.value == Accidental.NATURAL.value:
                return True
            elif self.value == Accidental.NATURAL.value and other.value == Accidental.NONE.value:
                return True
            else:
                return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(0) if self == Accidental.NONE else hash(self.value)


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
        NoteName('D', Accidental.FLAT),
        NoteName('D'),
        NoteName('E', Accidental.FLAT),
        NoteName('E'),
        NoteName('F'),
        NoteName('G', Accidental.FLAT),
        NoteName('G'),
        NoteName('A', Accidental.FLAT),
        NoteName('A'),
        NoteName('B', Accidental.FLAT),
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
    mode: Mode
    scale: typing.Sequence[Note]

    def __init__(self, root: NoteName, mode: Mode) -> None:
        self.root = root.note
        self.mode = mode

        diatonic_root = self.root - DIATONIC_SCALE[mode]
        self.scale = [
            (diatonic_root + offset) % 12
            for offset in rotate(mode, DIATONIC_SCALE)
        ]

        self.names = [None] * 12

        # every note in the scale should have a unique letter name
        letters = [
            chr(ord('A') + (ord(root.letter) - ord('A') + i) % 7)
            for i in range(7)
        ]

        for note, letter in zip(self.scale, letters):
            for accidental in Accidental:
                candidate = NoteName(letter, accidental)
                if candidate.note == note:
                    self.names[note] = candidate
                    break
            else:
                assert False, f"could not label note {note} with {letter}"

        unused = (i for i in range(12) if i not in self.scale)
        for offset in unused:
            # notes that aren't in the scale get their standard name
            self.names[offset] = ChromaticScale.name(offset)
        
        assert all(name is not None for name in self.names)
    
    def name(self, note: Note) -> NoteName:
        return self.names[note % 12]
    
    def engrave(self, note: Note) -> EngravingInfo:
        octave, index = divmod(note, 12)
        template = self.name(note)
        if note % 12 in self.scale:
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
        

class ChordKind(enum.IntEnum):
    MAJOR = 0
    MINOR = 1
    SEVENTH = 2
    DIMINISHED = 3

    @property
    def offsets(self):
        table = (0, 4, 7), (0, 3, 7), (0, 4, 10), (0, 3, 9)
        return table[self.value]

    def name(self, root: NoteName) -> str:
        if self == ChordKind.MAJOR:
            return str(root)
        elif self == ChordKind.MINOR:
            return str(root) + 'm'
        elif self == ChordKind.SEVENTH:
            return str(root) + '7'
        elif self == ChordKind.DIMINISHED:
            return str(root) + '°'


def accordion_chord(root: Note, kind: ChordKind) -> tuple[Note, Note, Note]:
    return tuple(root.note - 24 + offset for offset in kind.offsets)


CIRCLE_OF_FIFTHS = 'FCGDAEB'

def circle(i: int, mode: Mode = Mode.MAJOR) -> NoteName:
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


def invert(n: int, chord: tuple[Note, Note, Note]) -> tuple[Note, Note, Note]:
    for _ in range(n):
        chord = chord[1:] + (chord[0] + 12,)
    return chord