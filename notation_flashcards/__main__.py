import genanki
import html
import itertools
import pathlib

import tqdm

from notation_flashcards.theory import (
    ChordKind, KeySignature, Mode, Note, accordion_chord, circle, invert
)
from notation_flashcards.render import ScoreRenderer


pathlib.Path('images').mkdir(exist_ok=True)

deck = genanki.Deck(deck_id=1381930778, name='Accordion Chords')

nids = iter(itertools.count())

note_model = genanki.Model(
    model_id=1228304155,
    name='note',
    fields=[
        dict(name='NID'),
        dict(name='Key Signature'),
        dict(name='Note Name'),
        dict(name='Octave'),
        dict(name='Score'),
    ],
    templates=[
        dict(
            name='recall',
            qfmt='{{Score}}',
            afmt='{{Score}}<hr id="answer"><span style="font-size: 20px">{{Note Name}}</span><br>key signature: {{Key Signature}}<br>octave: {{Octave}}',
        ),
    ]
)

deck.add_model(note_model)

chord_model = genanki.Model(
    model_id=1330235254,
    name='chord',
    fields=[
        dict(name='NID'),
        dict(name='Key Signature'),
        dict(name='Chord Name'),
        dict(name='Inversion'),
        dict(name='Staff'),
        dict(name='Score'),
    ],
    templates=[
        dict(
            name='recall',
            qfmt='{{Score}}',
            afmt='{{Score}}<hr id="answer"><span style="font-size: 20px">{{Chord Name}}</span><br>key signature: {{Key Signature}}<br>inversion: {{Inversion}}',
        ),
    ]
)

deck.add_model(chord_model)

media_files = []

keysigs = itertools.chain(
    (KeySignature(circle(0), mode=Mode.MAJOR),),
    itertools.chain.from_iterable(
        (
            KeySignature(circle(i), mode=Mode.MAJOR),
            KeySignature(circle(-i), mode=Mode.MAJOR),
        )
        for i in range(1, 8)
    )
)

roots = [circle(i) for i in itertools.chain(range(0, 6), range(-6, 0))]

for keysig in tqdm.tqdm(keysigs, total=15, desc="Key Signatures"):
    for note in tqdm.trange(-24, 24, leave=False, desc="Notes"):
        octave = note // 12

        nid = format(next(nids), '06d')

        media_path = f'images/score_{nid}.png'
        media_files.append(media_path)
        staff = 'bass' if octave < 0 else 'treble'

        with ScoreRenderer(keysig, media_path) as renderer:
            renderer.add_note(note, staff)

        note = genanki.Note(
            model=note_model,
            fields=[
                str(nid),
                html.escape(str(keysig.name(keysig.root))),
                html.escape(str(keysig.name(note))),
                str(octave),
                f'<img src="score_{nid}.png">',
            ],
            due=int(nid),
        )

        deck.add_note(note)

    iterable = itertools.product(roots, (0, 1, 2), ('bass', 'treble'), ChordKind)
    total = 12 * len(ChordKind) * 3 * 2

    for root, inversion, staff, kind in tqdm.tqdm(iterable, total=total, leave=False, desc="Chords"):
        nid = format(next(nids), '06d')

        chord = accordion_chord(root, kind)
        if staff == 'treble':
            chord = tuple(note + 24 for note in chord)

        chord_name = kind.name(root)

        media_path = f'images/score_{nid}.png'
        media_files.append(media_path)

        with ScoreRenderer(keysig, media_path) as renderer:
            renderer.add_chord(invert(inversion, chord), staff)

        note = genanki.Note(
            model=chord_model,
            fields=[
                str(nid),
                html.escape(str(keysig.name(keysig.root))),
                html.escape(chord_name),
                str(inversion),
                staff,
                f'<img src="score_{nid}.png">',
            ],
            due=int(nid),
        )

        deck.add_note(note)

package = genanki.Package(deck, media_files)
package.write_to_file('accordion.apkg')