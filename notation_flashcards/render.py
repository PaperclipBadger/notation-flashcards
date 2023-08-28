import typing

from neoscore.common import *

from notation_flashcards import theory


neoscore.setup()

def render_chord(
    keysig: theory.KeySignature,
    chord: tuple[theory.Note],
    staff: typing.Literal['treble', 'bass'],
    path: str,
) -> None:
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

    Barline(ZERO, group)

    if staff == 'treble':
        staff = treble
    else:
        staff = bass

    Chordrest(staff.unit(4), staff, [str(keysig.engrave(note)) for note in chord], (1, 4))

    # neoscore forgets to close its file handles, so use bytearray
    neoscore.render_image(rect=(-Mm(23), -Mm(5), Mm(45), Mm(35)), dest=path, wait=True)

    # reset, but don't tear down Qt (because it throws a bunch of error messages and takes ages to boot)
    neoscore.document = Document(neoscore.document.paper)
    neoscore.app_interface.clear_scene()

