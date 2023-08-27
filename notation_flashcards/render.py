import pathlib

from neoscore.common import *

from notation_flashcards import theory



def render_chord(keysig: theory.KeySignature, chord: tuple[theory.Note], path: pathlib.Path) -> None:
    neoscore.setup()
    group = StaffGroup()
    width = Mm(20)

    assert keysig.mode in (theory.Mode.MAJOR, theory.Mode.MINOR)

    root_name = keysig.name(keysig.root)
    keysig_string = ''.join(
        (
            root_name.letter.lower(),
            root_name.accidental.neoscore,
            '_major' if keysig.mode == theory.Mode.MAJOR else '_minor',
        )
    )

    treble = Staff(ORIGIN, None, width, group)
    Clef(ZERO, treble, 'treble')
    KeySignature(ZERO, treble, keysig_string)

    bass = Staff((ZERO, treble.unit(8)), None, width, group)
    Clef(ZERO, bass, 'bass')
    KeySignature(ZERO, bass, keysig_string)

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
    scale = theory.KeySignature(theory.NoteName('C'), theory.Mode.MAJOR)
    chord = (0, 4, 7)
    render_chord(scale, chord, 'a.png')
    print('a', [str(scale.name(i)) for i in chord])

    scale = theory.KeySignature(theory.NoteName('C', theory.Accidental.SHARP), theory.Mode.MAJOR)
    chord = (-3, -4, -7)
    render_chord(scale, chord, 'b.png')
    print('b', [str(scale.name(i)) for i in chord])