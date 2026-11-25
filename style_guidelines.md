# Style guidelines: Florian Ulrich Jehn

How to make things that look and sound like Florian's work: presentations, plots, websites, posters, documents. Written for LLM assistants (and humans) working on his **own** projects, i.e. his work as an independent researcher, his blog/living literature review and his personal website. ALLFED and FernUniversität Hagen work keeps those institutions' branding. Only the writing section applies there.

Florian researches global catastrophic risk, food systems in catastrophes, nuclear winter, polycrisis and societal collapse. Website: https://florianjehn.github.io/ · Blog: https://florianjehn.github.io/Societal_Collapse/

**Files in this folder**
- `independent_researcher_template_v2.pptx`: slide template in this style (built by `src/build_template.py` from the older `independent_researcher_template.pptx`; the octagon shapes come from `src/octagon_motif.py`)
- `scientific_v2.mplstyle` + `src/plot_style.py`: matplotlib style, font and colormaps. `plot_demo.png` shows the result
- `src/palette.py`: all colour and font tokens in one place
- `assets/fonts/DidactGothic-Regular.ttf`: free fallback font (SIL Open Font License, `OFL.txt`)

---

## 1. The idea in one paragraph

Clean, calm, uncluttered. A warm paper background, one geometric typeface, and muted berry tones as the only real colour. The look borrows from three sources: **Japandi** (warm neutrals, lots of empty space, nothing decorative without a reason), **Bauhaus** (a clear grid, flat geometric shapes, function first) and **Art Deco** (as a hint: hairlines, double outlines, a chamfered corner). **The octagon is the signature shape**: it frames pictures, numbers, quotes and the thank-you, and echoes as a hairline outline. Without it the design looks like any corporate template, so use it on every slide type that has room for it. **Angles over curves**: corners are cut at 45°, never rounded. If an element could be removed without losing meaning, remove it.

## 2. Colour

### Tokens

| Role | Name | Hex | Use |
|---|---|---|---|
| Background | Paper | `#F7F4EF` | Default background for slides, web, plots |
| Tint | Pale mauve | `#EFE7E9` | Panels, tinted slides, table header band on web |
| Text | Ink | `#2E2A2B` | Body text (warm charcoal, never pure black) |
| Text | Muted | `#6E6668` | Secondary text, captions, credits, axis labels |
| Line | Hairline | `#D9D2CF` | Rules, table lines, grid lines, dividers |
| **Primary** | **Aubergine** | `#5D2A42` | Titles, key rules, the one highlighted value |
| Dark | Deep aubergine | `#3E1C2C` | Darkest step of ramps; rarely on its own |
| Secondary | Berry | `#8E5A74` | Bullets, lead text, links, column headers |
| Accent | Rose | `#CC8FA0` | Decorative accents only (title rule), never text |
| Light | Mauve | `#C9B1BD` | De-emphasized data, octagon outlines and echoes, second rule |
| Data | Slate | `#46708A` | Second data series |
| Data | Sage | `#627F64` | Fourth data series |
| Data | Ochre | `#C9A55A` | Fifth data series |
| Data | Context grey | `#A29A97` | "Other"/context data, never a category of its own |

The aubergine and mauve are the colours of Florian's current website.

### Rules
- **Berry tones are accents, not fills.** Most of every page is paper and ink. One strong colour per slide is enough; aubergine for the title is already one.
- **Highlight by contrast, not by an extra colour**: everything else in mauve or context grey, the one thing that matters in aubergine. No signal colours (no red/green/teal).
- Colours stay muted. Never brighten or saturate the tokens, never use pure black, pure white backgrounds or neon.
- Contrast on paper (WCAG): ink 12.9:1, aubergine 10.2:1, berry 5.0:1, muted 5.1:1. These four are safe for text at any size. **Rose (2.4:1) and mauve (1.8:1) are never used for text** that has to be read.
- Text on aubergine: paper colour (10.2:1). Use aubergine backgrounds only for small elements (a tag, a button), not full slides.
- Gradients, shadows, glows, glass effects: none.

## 3. Typography

- **One typeface: Century Gothic.** Geometric, round, open, elegant. Everything else follows its character.
- Fallbacks in this order: **Didact Gothic** (free, Google Fonts, closest match, bundled in `assets/fonts/`) → URW Gothic (Avant Garde clone, comes with Linux/Ghostscript) → Questrial → system sans-serif. Don't fall back to Quicksand (rounded ends) or to Arial/Helvetica unless nothing else exists.
- CSS stack: `font-family: "Century Gothic", "Didact Gothic", "URW Gothic", "Questrial", sans-serif;`
- **No bold for emphasis.** Hierarchy comes from size, colour and space. Didact Gothic has only one weight, so faux-bold looks smudgy. Bold is acceptable only in tiny functional spots in PowerPoint with real Century Gothic (presenter name, table total).
- No italics for emphasis either; italics only for titles of works and species names.
- **Sentence case** for all titles and headings (*"How much food is there?"*), never Title Case.
- **Small labels** (kicker above a title, section labels, footer, date, slide number, web nav) in **letter-spaced capitals**: 9 pt on slides, ~0.2 em tracking (`spc="200"` in pptx, `letter-spacing: 0.18em; text-transform: uppercase;` on the web), in aubergine or muted. Only for labels of a few words, never for sentences.
- Sizes on slides (16:9): title 28 pt, body 18 pt (16 pt for second level and dense slides), captions/credits 8–10 pt, statement/quote 24–28 pt, key numbers 40+ pt. Line spacing body ~1.1.
- Generous whitespace instead of lines and boxes. Left-aligned text; centred only on statement, quote and closing slides.
- Numbers: space before % (`10 %`), `~` for approximations, `×` for multiples, thin, readable digits (Century Gothic's are fine).

## 4. Shapes and ornament (the angular language)

The octagon carries the identity. A clean slide with only hairlines looks corporate; a clean slide with one clear octagon looks like Florian's. Always use **regular** octagons (pptx `octagon` preset with `adj` 29289, all sides equal; CSS `clip-path: polygon(29.3% 0, 70.7% 0, 100% 29.3%, 100% 70.7%, 70.7% 100%, 29.3% 100%, 0 70.7%, 0 29.3%)`), never stretched ones. Everything inside or around an octagon sits on its exact centre: nested octagons share one centre, and text in an octagon is centred optically (no inherited paragraph spacing; digits lifted, quote marks lowered slightly, see `src/octagon_motif.py`). Check this on the render.

**Octagon uses** (one or two per slide):
- **Octagon picture**: title and contact pictures (and portraits) are cropped to a large square octagon, with an **echo**: a mauve hairline octagon around it, ~0.2 in larger on every side and on exactly the same centre. Never offset.
- **Double octagon**: a pale mauve filled octagon inside a slightly larger mauve hairline one. Section numbers, the closing slide, the right half of a title slide without picture.
- **Filled octagon**: key numbers (pale mauve; the one that matters may be aubergine with paper text), the quote mark (aubergine with a paper-coloured “).
- **Slide number badge**: the slide number sits in a small hairline octagon in the header.
- **Corner ornament**: two concentric mauve hairline octagons (~2.8 and 2.5 in), mostly off the slide at the bottom right, so only a small corner of them shows. Only on text slides (content, tinted, statement, section, quote), never behind charts, tables or figures.
- **Octagon mark**: the small filled aubergine octagon at the end of the title rule.

The rest of the kit:

1. **Hairlines**: 0.75–1 pt lines in hairline grey or mauve to separate things. Prefer space over lines; prefer lines over boxes.
2. **Title rule with octagon mark**: a short rose rule (~0.55 in, 1.5 pt) under the title ending in a small filled aubergine octagon (~0.12 in). Once per slide.
3. **Chamfered corner**: panels, cards, image frames and buttons may have **one** corner cut at 45° (pptx preset `snip1Rect`, CSS `clip-path`). Never rounded corners, nowhere (`border-radius: 0`).
4. **Octagon**: replaces every circle or ring (see the list above). Never a circle.
5. **Double rule** at the bottom edge: an aubergine hairline with a thinner mauve hairline below it. The only Art Deco reference that is always visible, and it is meant to be barely noticed.
6. **Thin vertical bar** (aubergine, ~3 pt) left of a statement headline.
7. Bullets are **small squares** (▪) in berry; second level an en dash (–).

Not allowed: rounded rectangles, circles as decoration, pill-shaped buttons, drop shadows, icons as decoration, clip art, stock gradients, sunbursts/fans or other loud Deco motifs, more than one ornament type per element.

## 5. Layout

- Bauhaus grid: a 12-column grid with fixed margins (slides: 0.6 in left/right, title baseline at ~1.8 in, content from ~2.15 in). Align everything to it; asymmetric layouts (text left, figure right) are welcome.
- **Leave space empty.** A slide or section that is 40 % empty is fine. Don't fill space with decoration or bigger text.
- One idea per slide/section. When in doubt, split.
- Picture and text side by side, not text on top of pictures. If text has to sit on a photo, use a solid paper or aubergine block behind it, not a gradient.
- Consistent footer/header on content slides: slide number · date · talk title | event (spaced caps, muted), double rule at the bottom.

## 6. Pictures and figures

- Natural colours (they carry information, e.g. satellite images), but **prefer calm, low-saturation pictures** that sit well next to the muted palette. No filters, duotones or heavy desaturation unless Florian asks.
- Sharp rectangular crops; optionally one chamfered corner; never rounded corners or circular crops (portraits get an octagon or a rectangle).
- A picture has to show what the slide means (a trading floor for "financial system", not a building facade). Abstract list slides benefit from a picture next to the bullets.
- **Every picture needs a credit** (logos excepted): 8 pt muted text directly under the picture or in a bottom corner, e.g. `Image: NASA, Apollo 8 (restored by Toby Ord, tobyord.com/earth)`, `Figure: Xia et al. 2022, Nature Food (CC BY 4.0)`, `Own figure`. Check the source and license before using a picture; if unclear, ask Florian.
- Figures: prefer Florian's own redrawn figures over dense figures cropped from papers. Redraw key figures in the plot style below and make them large enough to read.
- Figures with a white background on paper slides: give them a thin hairline frame or, better, redraw them with the paper background.

## 7. Presentations

Use `independent_researcher_template_v2.pptx` (16:9, 13.33 × 7.5 in). Its example slides show how each layout is meant to be used. Layout names are unchanged from v1, so existing build scripts still work: `IR Title`, `IR Title no Image`, `IR Section`, `IR Content`, `IR Content Tinted`, `IR Content Image`, `IR Two Columns`, `IR Statement`, `IR Statement Image`, `IR Panel Text`, `IR Panel Image`, `IR Text Chart`, `IR Text Table`, `IR Image Grid`, `IR Key Numbers`, `IR Quote`, `IR Title Only` (full-width figures), `IR Contact`, `IR Closing`.

- Background paper everywhere; `IR Content Tinted` (pale mauve) sparingly, e.g. for a summary slide.
- Pictures on `IR Title` and `IR Contact` are cropped to a square octagon by the layout. Use landscape or square photos with the subject in the centre; the corners get cut off.
- Native pptx charts: mauve bars with one aubergine bar; lines aubergine → slate → rose; doughnuts only for ≤5 parts. Tables have no fills: aubergine header text, hairlines between rows.
- Contact details in the template are placeholders (`florian@example.org`, `www.example.org`); ask Florian for the real ones.
- If Century Gothic is missing on the rendering machine, LibreOffice substitutes something else. For faithful renders map it to Didact Gothic with a fontconfig file:
  ```xml
  <fontconfig>
    <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
    <dir>/path/to/assets/fonts</dir>
    <match target="pattern"><test name="family"><string>Century Gothic</string></test>
      <edit name="family" mode="assign" binding="strong"><string>Didact Gothic</string></edit></match>
  </fontconfig>
  ```
  then `FONTCONFIG_FILE=fonts.conf soffice --headless --convert-to pdf …`. Didact Gothic runs slightly narrower than Century Gothic, so leave some room in text boxes.
- Check every render for overflow, leftover placeholder text, missing credits and anything that breaks the rules above (rounded corners, extra colours, bold).
- Text on slides follows section 10: few words, conversational titles, details in the speaker notes.

## 8. Plots

```python
import sys; sys.path.insert(0, "src")   # or run from src/
from plot_style import use_style
use_style()              # paper background, for slides and web
use_style(white=True)    # white background, for journal figures
```
`use_style` registers Didact Gothic, the colormaps `berry`, `berry_slate` (and `_r` versions) and loads `scientific_v2.mplstyle`. In plain matplotlib, `plt.style.use("scientific_v2.mplstyle")` works too (font only if Century Gothic or Didact Gothic is installed).

- **Categorical order: aubergine, slate, rose, sage, ochre.** Checked with simulated deuteranopia and protanopia (minimum CIELAB distance ~19 between any two). Max five categories; with more, group the small ones into "Other" in context grey, use small multiples or label directly.
- **Highlight**: everything mauve/context grey, the key series or bar aubergine.
- **Sequential** data and maps: `berry` (paper → aubergine). **Diverging**: `berry_slate` (slate ↔ paper ↔ aubergine). Built-in fallback: `RdPu` (sequential), `PuOr` (diverging). No rainbow/jet.
- Horizontal grid hairlines only; **no vertical grid lines through bars**. No box around the axes; only a bottom hairline. No tick marks.
- Lines 1.8 pt with **square ends and mitred joins** (angular); markers small; no marker outlines.
- **Label lines directly** at their ends instead of a legend wherever possible. If a legend is needed: no frame.
- Titles left-aligned in aubergine, in sentence case, ideally stating the finding (*"Yields drop by a third in the first year"*). Axis labels muted with units in parentheses.
- Maps: Winkel Tripel projection (display only), coastlines as hairlines in muted grey, no graticule labels unless needed.
- Export: PNG at 300 dpi for slides/web, PDF/SVG for papers. Figure size for a full-width slide figure: 12 × 5.5 in.
- Every figure gets a source line (see section 6) where it is used.

## 9. Websites

The personal website (Beautiful Jekyll) already uses Century Gothic and aubergine/mauve. Bring it and any new pages in line with these tokens:

```css
:root {
  --paper: #F7F4EF;  --tint: #EFE7E9;  --ink: #2E2A2B;  --muted: #6E6668;
  --hairline: #D9D2CF;  --aubergine: #5D2A42;  --berry: #8E5A74;
  --rose: #CC8FA0;  --mauve: #C9B1BD;
  --font: "Century Gothic", "Didact Gothic", "URW Gothic", "Questrial", sans-serif;
  --chamfer: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 0 100%);
}
body { background: var(--paper); color: var(--ink); font-family: var(--font);
       font-size: 1.0625rem; line-height: 1.6; }
h1, h2, h3 { color: var(--aubergine); font-weight: 400; letter-spacing: 0.01em; }
h2::after { content: ""; display: block; width: 3rem; height: 2px;
            margin-top: 0.5rem; background: var(--rose); }
a { color: var(--berry); text-decoration-thickness: 1px; text-underline-offset: 3px; }
a:hover { color: var(--aubergine); }
.label, nav a { font-size: 0.78rem; letter-spacing: 0.18em; text-transform: uppercase; }
.card { background: var(--tint); clip-path: var(--chamfer); padding: 1.5rem; }
* { border-radius: 0 !important; box-shadow: none !important; }
.octagon { clip-path: polygon(29.3% 0, 70.7% 0, 100% 29.3%, 100% 70.7%,
            70.7% 100%, 29.3% 100%, 0 70.7%, 0 29.3%); }  /* avatar, key numbers */
hr { border: 0; border-top: 1px solid var(--hairline); }
footer { border-top: 1px solid var(--aubergine);
         box-shadow: 0 4px 0 -3px var(--mauve) !important; }
```
- Load Didact Gothic from Google Fonts (`family=Didact+Gothic`) as the web fallback; Century Gothic is used where it is installed.
- Content width ~42 rem for text, single column, generous vertical space between sections. Lists of papers/talks as plain hairline-separated lists, not cards with images.
- Buttons: text links or rectangular outlined buttons (1 px aubergine border, spaced caps label), optionally chamfered. No pills, no rounded corners.
- Header/nav: paper background, aubergine name in regular weight, spaced-caps nav links. No big hero images; if one is used, it's calm, full-width, rectangular, with a credit.
- Dark mode (if needed): background `#241A1F`, text `#EDE6E8`, headings mauve `#C9B1BD`, links rose `#CC8FA0`, hairlines `#4A3C42`.
- Must work at phone width without horizontal scrolling.

### Bringing florianjehn.github.io in line (checked 2026-11-14)

The site runs on Beautiful Jekyll. Today it has a cool grey page (`#EEEEEE`), text `#404040`, mauve navbar and footer bands (`#C9B1BD`) with grey borders, aubergine links, Quicksand loaded first, small radii on buttons/code, a round avatar with drop shadow configured in the theme, and italic grey blockquotes. To migrate:

1. `_config.yml`:
   ```yaml
   page-col: "#F7F4EF"
   text-col: "#2E2A2B"
   link-col: "#8E5A74"
   hover-col: "#5D2A42"
   navbar-col: "#F7F4EF"
   navbar-text-col: "#5D2A42"
   navbar-border-col: "#D9D2CF"
   footer-col: "#F7F4EF"
   footer-text-col: "#6E6668"
   footer-link-col: "#8E5A74"
   footer-hover-col: "#5D2A42"
   round-avatar: false
   site-css:
     - "/assets/css/florian.css"
   ```
2. Replace the Quicksand Google Fonts link with `family=Didact+Gothic` and set the font stack to the one in section 3 (body and `.navbar-custom`).
3. Put the CSS block above into `assets/css/florian.css`. Add `blockquote { font-style: normal; color: var(--muted); border-left: 3px solid var(--mauve); }`.
4. The mauve navbar band is the one thing that is part of the current identity. Moving it to paper with a hairline is calmer (Japandi). Keeping a thin mauve band is acceptable if Florian prefers it.

## 10. Writing like Florian (slides, notes, blog, web copy)

Everything written for Florian must sound like him, not like a polished AI summary. Before writing a lot of text, read a few posts of his living literature review (https://florianjehn.github.io/Societal_Collapse/). Check every slide/paragraph: *"would Florian say this out loud in a talk?"* If it sounds like a press release, rewrite it.

**Titles**
- Short and conversational. Mix these types:
  - a question: *"Are famines over?"*, *"How much food is there?"*, *"Wait, we can go extinct?"*, *"So, where should you stay?"*
  - a blunt statement: *"It gets dark"*, *"It gets cold fast"*, *"Trade collapses"*
  - the finding as a statement: *"No place is safe against all kinds of catastrophe"*
  - a plain label for sections: *"Communication"*, *"Summing it up"*
  - occasionally playful or pop culture: *"Enter dramaturgy"*, *"Hot 2020s"*, *"Gotta catch 'em all"*, *"Quantitative history to the rescue"*
- A series of related slides uses an arrow: *"Understanding Risk→Hazard"*, *"Why is systemic risk management so hard? →Uncertainty"*.

**Slide text**
- **Less text than you think.** Aim for 3–4 bullets of ~3–7 words each (never more than one line at 20 pt), 1–2 short lines for statement/quote slides. Dates, names, extra numbers, examples and side details go into the speaker notes, not onto the slide. If a bullet needs a sub-bullet or wraps to a second line, cut it or move half of it to the notes.
- Bullets are fragments: no full stop at the end, often no verb (*"Grows quickly / Low tech / Used in many countries already"*). The figure carries the slide.
- Useful list formats:
  - `→` for cause/effect and chains (*"Limits to Growth → You run out of resources"*)
  - *"Term: plain explanation"* for definitions; *"Main idea: Resources are limited!"*
  - `>` rankings (*"Southern Hemisphere > Northern Hemisphere"*, *"Rural > urban"*)
  - Claim/Response or too broad / too specific contrasts
- An occasional `!` on the key point.
- Numbers with context: *"1.6 million shelter places (so ~2.5 % of the population)"*. Deadpan versions welcome (*"of these 579 exactly 0 are usable"*, *"ten out of ten"*). Space before %; `~` for approximations.
- Full reference at the bottom of the slide whenever a figure or finding comes from a paper. **Never add "(own work)" to cited papers or figure credits**, also not for Florian's own papers.
- Examples of real slides:
  - *"Understanding Risk→Hazard"*: "The thing that will mess up your day. Comes in two main flavors: Gradual + Release < -- > Rapid Shock"
  - *"Things that do not cause collapse→bad luck?"*: "Every year society faces random hazards / Play long enough and you die / Kinda true? / Partly, but we need more / Resilience is the other side of the coin"
  - *"Limits to Growth (1972)"*: "Main idea: Resources are limited! / Is this one correct? / We'll probably know in a few years in which scenario we are in"
  - *"Nuclear winter is a real possibility"*: "As long as we don't know how much soot burning down New York would create, we cannot discard nuclear winter / … Seems sus to me / So, what happens if we end up in a nuclear winter?"
  - *"Seaweed as a resilient food"*: "Grows quickly / Low tech / Used in many countries already"

**Voice**
- Ask the audience questions (*"But what is collapse even?"*, *"Is this one correct?"*). Talk to them as "you" and answer objections before they're raised (*"You might think: 'But can't I just stockpile all of this?'"*, *"But do you? Do you think you could run a farm…?"*).
- Present studies one at a time: what they did (concretely) → what they found → the catch. In notes as bullets: *"X et al.: did … / found … / catch: …"*.
- Put the catch right after the claim: *"Unfortunately, it does not tell you how close you are"*, *"Admittedly, this is a pretty extreme scenario"*, *"Obviously, only three data points, so not super reliable"*, *"(mostly)"*, *"Kinda true?"*, *"Partly, but we need more"*.
- Be open about the limits of what he knows: *"I'm not a historian, so take this with a grain of salt"*, *"I could not find any study on X"*, *"This is more speculative"*.
- Take sides, first person: *"I think"*, *"Seems sus to me"*, *"This argument does not make much sense to me, as…"* (with a concrete counterexample). Criticise the sources too: *"what I found perplexing about this book is how timid it is"*. Fairness comes out dry: *"to be fair, progress wasn't stellar before they showed up either"*.
- Define jargon in one plain line the first time (*"This is called a critical transition."*), with an everyday picture if there is one (ball in a landscape, politics as theatre, *"think of each parameter as a knob"*).
- Small "Imagine…" stories make the abstract concrete (a person born in Ugarit in 1230 BC; a fishing village that turns into Goliath; a 2075 scenario). One per section at most.
- Openers: a personal or concrete hook (*"Recently, I visited a cold war bunker…"*), a short punchy line (*"Life feels more rough, because it is."*) or a question (*"What would we eat if the sun disappeared tomorrow?"*), then *"In this talk I want to…"*.
- Closers are short and literal, sometimes a call to action: *"Collapse is about preparation, not luck (mostly)"*, *"It's complicated (but likely still Australia)"*, *"The largest future risk for humanity is humanity."*, *"We all stand and fall together."*, *"Now we just have to put in the work."*
- Humour is understatement, not jokes: dry asides in parentheses, one-word punchlines (*"Easy."*), sarcasm aimed at institutions (*"Looking at you Germany."*, *"It's always Ronald Reagan, isn't it?"*), self-deprecation, the occasional pop-culture nod. Use it sparingly; less for policy/expert audiences.
- **No swearing in course or teaching material.** Mild swearing is part of his blog voice, but in talks only if he asks for it.
- Typical phrases: *"The tricky thing is…"*, *"pretty much"*, *"quite"*, *"super"*, *"kind of"*, *"Obviously"*, *"Unfortunately / Thankfully"*, *"Interestingly"*, *"So,"*, *"Still,"*, *"Though,"*, *"This means"*, *"Or said differently"*, *"think X, Y, Z"*, *"we are in for a rough ride"*, *"have a bad time"*, *"really, really bad"*, *"my two cents"*, *"Don't get me wrong"*.
- Recurring themes: inequality, democracy, cooperation and resilience, argued openly from his (left) position (critique of neoliberalism, UBI, citizens' assemblies). Link back to them where it fits naturally; don't force it.
- Spelling: -ize/-yze (civilization, organize, analyze). Never -ise. His own "focussed"/"modelling" are fine.
- Register by audience: courses and public talks are casual. Policy and expert talks stay plain and first person, with fewer jokes, more careful hedging and explicit research gaps.
- German texts: same casual register, with English terms where they are the normal ones.

**Speaker notes**: short, abstract bullet points, not prose or a script. 3–6 fragments that remind Florian what to say (the key point, the number, the catch, the transition): *"now to ASRS / Direkt bad, indirect worse / Explain mechanism"*, *"Landmark study by Coupe et al 2019 / key result: drop of almost ten degrees"*. A vignette is a single bullet (*"Imagine: Ugarit 1230 BC → ruin 80 years later"*). **Florian's own notes are ground truth**: once he has edited them, never overwrite them with drafted notes.

**Don't**
- No metaphorical aphorisms or poetic closers (*"Silence is a warning: if the filter lies ahead, it could be waiting for us too."*). Short literal closers are fine.
- No colons or em-dashes used as dramatic pivots (*"1945: The bomb"*, *"Obviously yes: the cost is trivial…"*, *"Lesson: …"*).
- No polished parallel card triads with abstract labels (*"Present harm / Narrow values / Who decides?"*) filled with full sentences. Use a plain bullet list next to a figure. Cards/timelines only when the content really is a sequence.
- No both-sides hedging (*"But: failure at the extreme does not make the core idea worthless."*). Say what Florian thinks.
- No full sentences with periods in bullets; no meta text on slides (*"How to use the boxes"*).
- Avoid AI-sounding vocabulary and constructions: crucial, landscape, lens (except his own "Uruway lense"), delve, underscores, profound, pivotal, nuanced, navigate, Moreover, Furthermore, Additionally, Importantly, "In short", "not only … but also", "it's not X, it's Y", "The question is not whether … but whether …", "reveals a fundamental tension".

## 11. Final checklist

- [ ] Paper background, ink text, berry only as accent; no colours outside the token table
- [ ] Century Gothic (or Didact Gothic) only; no bold/italics for emphasis; sentence case titles
- [ ] No rounded corners, circles, shadows or gradients anywhere
- [ ] One title rule with octagon mark per slide; at most one chamfered corner per element
- [ ] At least one octagon on every slide type that has room for it (title, section, key numbers, quote, closing, contact); octagons regular, not stretched
- [ ] Every picture has a credit; every finding has a reference
- [ ] Plots: ≤5 categories in the fixed order, direct labels, no vertical grid lines
- [ ] Text passes the "would Florian say this out loud?" test; bullets are short fragments
- [ ] Rendered and inspected (overflow, placeholder text, contrast)

## 12. Code conventions (for build scripts in Florian's projects)

Python only, following https://github.com/florianjehn/Scientific-Repository-Template: **uv** for environments (`uv sync`, `uv run python src/<module>.py`, `uv add <package>`; never conda or bare pip), Python 3.13, reusable logic in `src/`, PEP 8 + Ruff (line length 88, rules E/F/I), short functions with docstrings (summary, `Arguments:`, `Returns:`), `print()` instead of logging, no unit tests (outputs are checked visually), never claim code works without running it and inspecting the output.
