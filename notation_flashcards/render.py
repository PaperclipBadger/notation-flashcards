from types import TracebackType
import typing
import contextlib

from neoscore.common import *

from notation_flashcards import theory


neoscore.setup()


_score_exists = False


class ScoreRenderer(contextlib.AbstractContextManager):
    def __init__(self, keysig: KeySignature, path: str) -> None:
        global _score_exists
        assert not _score_exists, "Only one Score object can exist at a time"

        assert keysig.mode in (theory.Mode.MAJOR, theory.Mode.MINOR)

        self.keysig = keysig
        self.path = path

        self.group = StaffGroup()

        width = Mm(20)

        root_name = keysig.name(keysig.root)
        keysig_string = ''.join(
            (
                root_name.letter.lower(),
                root_name.accidental.neoscore,
                '_major' if keysig.mode == theory.Mode.MAJOR else '_minor',
            )
        )

        self.treble = Staff(ORIGIN, None, width, self.group)
        Clef(ZERO, self.treble, 'treble')
        KeySignature(ZERO, self.treble, keysig_string)

        self.bass = Staff((ZERO, self.treble.unit(8)), None, width, self.group)
        Clef(ZERO, self.bass, 'bass')
        KeySignature(ZERO, self.bass, keysig_string)

        Brace(self.group)
        SystemLine(self.group)

        Barline(ZERO, self.group)

    def add_note(self, note: theory.Note, staff: typing.Literal['treble', 'bass']) -> None:
        self.add_chord((note,), staff)

    def add_chord\
        ( self
        , notes: typing.Iterable[theory.Note]
        , staff: typing.Literal['treble', 'bass']
        ) -> None:
        if staff == 'treble':
            staff = self.treble
        else:
            staff = self.bass

        Chordrest(staff.unit(4), staff, [str(self.keysig.engrave(note)) for note in notes], (1, 4))

    def __enter__(self) -> Any:
        return super().__enter__()
    
    def __exit__\
        ( self
        , __exc_type: type[BaseException] | None
        , __exc_value: BaseException | None
        , __traceback: TracebackType | None
        ) -> bool | None:
        global _score_exists
        assert _score_exists

        neoscore.render_image(rect=(-Mm(23), -Mm(5), Mm(45), Mm(35)), dest=self.path, wait=True)

        # reset, but don't tear down Qt (because it throws a bunch of error messages and takes ages to boot)
        neoscore.document = Document(neoscore.document.paper)
        neoscore.app_interface.clear_scene()
        _score_exists = False

        return super().__exit__(__exc_type, __exc_value, __traceback)