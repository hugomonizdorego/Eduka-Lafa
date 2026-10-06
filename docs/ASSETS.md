# Character asset provenance

Reference: user-supplied `Edukasaun Logo.png`. The original logo file is not
included in this repository. Preserve the source owner's rights to that identity.

The new transparent `lafa/assets/lafa-atlas.png` was created using the built-in
ImageGen tool for this LAFA project. It retains the recognizable green crocodile,
large round green glasses, cream belly, dark green back spikes and blue book
with the Timor-Leste flag. All original lettering and the circular logo frame
were removed. No original logo text is present in the atlas.

Production prompt:

> Create a transparent 3-by-3 atlas of the same full-body friendly crocodile
> from the supplied logo: idle holding a closed blue book, reading an open book,
> thinking with hand on chin, walking right, sitting with book, playing with
> a handheld controller, serious, mildly angry, and talking with a hand gesture.
> Preserve green glasses, cream belly, green spikes and the Timor-Leste flag
> on the blue book. Remove all text, circle border and background. Keep every
> pose separate, with complete head, feet and tail. Match the reference's
> polished 2D cartoon style and soft dimensional shading. No lettering,
> grid lines, labels, backgrounds or watermarks; actual transparent alpha.

`atlas.json` supplies measured regions around the actual rendered poses, with
transparent padding. Qt normalizes each region onto a 418-pixel square canvas
at runtime. The source atlas is kept intact. Screenshots/contact sheets use the
same renderer rather than regenerating character art.

Code license is MIT. Rights in the supplied brand identity remain with its owner.
The new atlas is included for this requested LAFA/Edukasaun OS project.

## Additional activities (0.2.0)

`lafa-activities.png` is a second transparent generated atlas, 1536×1024,
using the first LAFA atlas as the character reference. `activities.json`
supplies six measured regions normalized onto a 540-pixel square in Qt.
The image is kept intact; cropping/padding occurs only in the app renderer.

Production brief:

> Keep exactly the reference crocodile, glasses, cream belly, green spikes,
> blue book and polished cartoon shading. Create six separated full-body
> activities in a 3×2 atlas: sleeping on a pillow, bathing in an opaque
> tub with bubbles, sitting modestly on a toilet reading a book, studying
> at a desk with an open book and pencil, eating a healthy lunch with
> an apple, and stretching happily. No explicit anatomy or bodily waste.
> Preserve complete tails, feet and props. No lettering, watermark,
> grid lines or background. True transparent alpha.

The supplied desktop reference guided the floating bubble/input pattern.
No Microsoft/Clippy character or Windows screenshot is bundled.

## Traditional clothing and dance poses (0.3.0)

`lafa-traditional.png` is a transparent 1254×1254 generated atlas. The user's
supplied photograph of traditional clothing (male subject on the right) guided
the striped red tais waist wrap, broad white sash, patterned head wrap and black
plume, bead necklaces, crescent chest pendant and upper-arm ornament. The human
photograph is not included in the repository.

Production brief:

> Preserve the friendly green LAFA crocodile, green round glasses, cream belly,
> dark green spikes and blue Timor-Leste book. Use the supplied male traditional
> outfit: red/burgundy striped tais wrap, white waist sash, patterned head wrap,
> tall dark plume, orange bead necklaces and silver crescent chest pendant.
> Create nine separated full-body poses in a transparent 3×3 atlas: welcoming
> wave, reading, thinking; walking, sitting, talking; studying at a desk,
> Tebe-tebe open-arm side-step and Bidu raised-arm bent-knee dance interpretation.
> Keep head, plume, feet and tail intact. No humans, labels, logo text, watermark,
> grid or background.

`traditional.json` contains measured rectangles normalized to a 440-pixel
canvas by Qt. The source bitmap is unmodified. All nine traditional poses were
visually inspected; the seventeen-activity sheet and traditional sheet are
rendered from the same app assets. Other activities use the earlier costume
artwork. Tebe/Bidu are playful mascot interpretations with procedural sway,
not a verified choreography or documentation of every Timorese tradition.
