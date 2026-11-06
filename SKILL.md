---
name: wrapped-recap
description: Builds a Wrapped-style, tap-through story page that recaps what someone did with Claude over a year or any other period, laid out month by month with stats, top genres and a playful personality title. Use whenever the user asks for things like "make me a Wrapped", "recap my year on Claude", "what have I done this year", "year in review", "monthly highlights of my chats", "look back at my 2026", or a recap of a shorter stretch such as "my summer on Claude" or "the last six months".
---

# Wrapped recap

Turn what Claude knows about the user into a shareable, tap-through recap page. The design is fixed in `assets/template.html`. Your job is to gather the facts, write the copy, and write one JSON object. You never edit HTML or CSS.

Files in this skill:

- `assets/template.html`: the page. Slides are rendered from a `const WRAPPED = {…}` object between `// ===== BEGIN WRAPPED DATA =====` and `// ===== END WRAPPED DATA =====`.
- `assets/example-data.json`: a complete fictional example. Read it before writing; match its shape and tone.
- `scripts/build.py`: fills the template with your JSON and checks the copy rules.
- `scripts/check_layout.mjs`: optional, checks every slide fits a 375×667 phone in light and dark mode (needs Playwright).

## Workflow

### 1. Gather

Work out the period first. Default to the current calendar year up to today; use whatever the user names instead ("my summer", "since I started the job").

Collect raw material from every source you have, in this order:

1. **Memory.** Read the user's memory or preference files and any saved notes about them.
2. **Past chats.** If a past-chats search tool exists, search it month by month across the period (for example "January 2026", then topic words that come up: "application", "course", "project", "trip", "learning"). Follow promising threads with a second search. Note the date of each conversation.
3. **The user.** If neither source exists, or the results are thin (fewer than roughly three months with anything in them), say so plainly and ask the user to paste notes or list a few highlights per month. Wait for their reply before building.

Never invent events, numbers, names or dates. If you didn't find it, it isn't on the page.

While gathering, also note:

- Spelling preference (UK or US). Look for it in memory, otherwise infer it from how the user writes. Set `lang` to `en-GB` or `en-US` to match.
- The user's first name, for the intro and outro. If you don't know it, write the headlines without a name ("Here’s your 2026 on Claude.").
- Whether the user has said they want direct or honest feedback (for the optional note slide).

### 2. Sort

Put each item in a month only when there is a date or strong evidence (the conversation date, a stated deadline, "I just passed…"). For anything undated:

- If it ran all year or you can't place it, put it on a "throughout the year" slide: type `month`, giant word `all`, headline like "All year, on repeat."
- If there's weak evidence for one month, place it there and tell the user in your reply that it's a guess.

Things still in progress at the end of the period go in the last month ("And you’re still going.").

### 3. Gaps

A month with nothing gets an honest "quiet season" slide: type `gap`, giant word `zzz` (or `…`, `shh`). Merge consecutive empty months into one slide ("February to May: off the record."). One or two sentences, no filler, no guessing what they were up to. Don't add a gap slide for months after today.

### 4. Privacy

The page must be safe to share. Leave out:

- health (physical or mental), including diagnoses, medication, therapy, symptoms and fitness tied to a condition
- money: salary, debt, benefits, purchases, finances
- relationships, dating, family conflict
- anything that could spoil a surprise (gifts, proposals, parties, unannounced plans)
- other people's private lives, including named friends, family or colleagues and what they're going through
- anything the user marked as private, plus legal matters and sensitive identity details

When in doubt, leave it out. Job applications, courses, certificates, projects, hobbies, trips and learning goals are usually fine; keep employer names only if they are public organisations.

In your chat reply, tell the user what *kinds* of things you left out (for example "I left out anything about health and money"), without listing the items.

### 5. Stats

Count only what's evidenced: job applications, certificates, courses finished, projects started or shipped, interviews prepped, talks given, books read. Never estimate or round up. Pick the 3–4 that mean the most for this user. Keep values short (ideally 1–3 characters, never more than 4) and labels to a few words. If a count covers less than the whole period, say so in the label ("jobs you went for, August to October").

In your chat reply, say that totals only reflect what Claude knows about.

### 6. Slides, in order

1. `intro`
2. one `month` slide per month with content, a `gap` slide per run of empty months, and an optional "all year" `month` slide after the last month
3. `stats`: year in numbers
4. `ranking`: top 5 genres (the five themes that took up most of the year, most first)
5. `personality`: a playful title, like "the Multi-Hyphenate" or "the Teacher Who Ships", with a short `lead` of 3–5 roles and one line of body
6. `note`: optional, see below
7. `outro`: send-off and replay button

Include the **note** slide only if the user's preferences say they want direct feedback, or they ask for it. Keep it kind and specific: one pattern you noticed, backed by things on the page, then one suggestion. Never about anything from the privacy list.

### 7. Copy rules

- Headlines: short and warm, about 2–8 words, ending with a full stop. "Builder mode." "Application season begins." "The month the ideas wouldn’t stop."
- 2–5 items per month, at most about 20 words each. Start with a verb or a noun, not "You". Specifics beat adjectives ("Passed your driving theory test", not "Made great progress").
- Sentence case everywhere. Curly apostrophes and quotes (’ “ ”), never straight ones.
- Match the user's spelling (colour/color, organise/organize, programme/program).
- Talk to the user as "you". Light humour, call-backs between months are good ("That January fire training? This is where it paid off.").
- No corporate or AI-sounding phrasing: avoid "journey", "embarked", "leveraged", "delved", "showcased", "testament", "navigated", "unlocked new levels", "a year of growth", exclamation marks, and emoji.
- Giant words: 2–5 characters, lowercase. Month abbreviations (`jan`), the year (`2026`), a stat number, `top 5`, `you`, `hmm`, `zzz`, the next year for the outro.

### 8. Build

Write the data as JSON (see the schema below and `assets/example-data.json`), save it as e.g. `wrapped-data.json`, then run:

```bash
python scripts/build.py wrapped-data.json wrapped.html
```

Fix every `error:` line, and every `warning:` line unless you have a good reason. Errors include neighbouring slides with the same background colour and leftover `[placeholder]` text.

**Colour combos.** Rotate through these so no two neighbouring slides share a background. Start with `plum/cobalt` and end with `plum/violet`:

`cobalt/plum`, `sun/tang`, `pink/sun`, `lilac/sun`, `mint/lilac`, `tang/sun`, `plum/violet`, `sun/pink`, `mint/sun`, `pink/lilac`, `lilac/pink`, `plum/cobalt`

These have been contrast-checked in light and dark mode. Don't invent others. If you leave `combo` out, the page picks one, but setting it yourself gives a better spread.

**Fit check.** Every slide must fit a 375×667 screen without text running into the Back/Next buttons. If Node and Playwright are available, run:

```bash
node scripts/check_layout.mjs wrapped.html
```

Trim copy on any slide reported as `OVERFLOW` or `tight`. If Playwright isn't available, the page auto-shrinks text a little to fit, but stay within the copy limits above: a month slide with 5 items of 20 words is the most that fits comfortably.

### 9. Deliver

- If you can publish artifacts, publish `wrapped.html` as an HTML artifact with the page's title.
- Otherwise save `wrapped.html` where the user can open it and present it.

Keep the chat reply to a few sentences:

- how to navigate: tap the right side or press → to go forward, tap the left side or press ← to go back
- which months were empty
- anything you placed by guesswork
- what kinds of things you left out, and that the numbers only reflect what Claude knows about

Offer to change anything: swap a highlight, rename the personality, add or drop the honest note.

## Data schema

```json
{
  "lang": "en-GB",
  "title": "Sam’s 2026, wrapped",
  "label": "Sam’s 2026 on Claude, a recap you tap through",
  "slides": [ { "type": "…", "giant": "…", "combo": "bg/shape", "headline": "…", … } ]
}
```

`title` becomes the page and tab title. `label` is read out by screen readers.

Every slide has `type`, `giant`, `headline`, and optionally `combo`. Extra fields per type:

| type | fields |
|---|---|
| `intro` | `body`: 1 short line; `hint`: "Tap to unwrap." |
| `month` | `items`: 2–5 strings; optional `body` |
| `gap` | `body`: 1–2 sentences |
| `stats` | `stats`: 3–4 of `{ "value": "14", "label": "jobs you went for" }` |
| `ranking` | `items`: exactly 5 strings |
| `personality` | `lead`: roles, full stops between; `body`: 1 line |
| `note` | `body`: 2 short paragraphs |
| `outro` | `body`: 1 line; `replay`: "Play it again" |

`body` is always an array of paragraphs. All text is inserted as plain text, so don't use HTML or Markdown.
