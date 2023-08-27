import pathlib

from neoscore.common import *

from notation_flashcards import theory



notes = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']


def render_chord(scale: theory.Scale, chord: tuple[theory.Note], path: pathlib.Path) -> None:
    neoscore.setup()
    group = StaffGroup()
    width = Mm(20)

    signature = notes[scale.root % 12] + '_major'

    treble = Staff(ORIGIN, None, width, group)
    Clef(ZERO, treble, 'treble')
    KeySignature(ZERO, treble, signature)

    bass = Staff((ZERO, treble.unit(8)), None, width, group)
    Clef(ZERO, bass, 'bass')
    KeySignature(ZERO, bass, signature)

    Brace(group)
    SystemLine(group)

    if sum(note >= 0 for note in chord) >= 2:
        staff = treble
    else:
        staff = bass

    Chordrest(staff.unit(4), staff, [str(scale.engrave(note)) for note in chord], (1, 4))

    neoscore.render_image(rect=None, dest=path, wait=True)
    neoscore.shutdown()


if __name__ == "__main__":
    scale = theory.WesternScale(0, theory.Mode.MAJOR)
    chord = (0, 4, 7)
    render_chord(scale, chord, 'a.png')
    print('a', [str(scale.name(i)) for i in chord])

    scale = theory.WesternScale(1, theory.Mode.MAJOR)
    chord = (-2, -4, -7)
    render_chord(scale, chord, 'b.png')
    print('b', [str(scale.name(i)) for i in chord])