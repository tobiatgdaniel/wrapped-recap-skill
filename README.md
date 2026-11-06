# Wrapped recap, a Claude skill

Ask Claude for "my year on Claude" and get back a tap-through, Wrapped-style story page: one slide per month, your year in numbers, your top five themes, a playful personality title, and an optional honest note. It works for any period, such as a year, a summer or the last six months.

## Install

**Claude apps (claude.ai, desktop, mobile)**

1. Go to **Settings → Capabilities** and make sure **Code execution and file creation** is on. Skills need it.
2. Under **Skills**, choose **Upload skill** and select `wrapped-recap.zip`.
3. Make sure the skill is switched on.

**Claude Code**

Unzip the folder into `~/.claude/skills/` (for all your projects) or `.claude/skills/` in a project, so you end up with `~/.claude/skills/wrapped-recap/SKILL.md`.

## Use it

Say something like:

- "Make me a Wrapped"
- "Recap my year on Claude"
- "What have I done this year?"
- "Monthly highlights of my chats since June"

Claude gathers what it knows, writes the slides, checks they fit on a phone screen, and gives you the page (as an artifact where available, otherwise as an HTML file).

## What it needs

It works best when Claude can see your history:

- **Memory** turned on, so Claude has notes about you, and/or
- **Past chats search** (reference past chats), so Claude can look back month by month.

Without either, Claude will ask you to paste notes or list a few highlights per month. It never makes things up: empty months get one honest "quiet season" slide.

## Privacy

The page is meant to be safe to share. Claude leaves out health, money, relationships, surprises, and other people's private lives, and tells you what kinds of things it left out. Numbers only count what Claude actually knows about.

## What's inside

```
wrapped-recap/
├── SKILL.md                 instructions Claude follows
├── assets/
│   ├── template.html        the page design (fills itself from one JSON object)
│   └── example-data.json    a fictional example year
└── scripts/
    ├── build.py             fills the template and checks the copy rules
    └── check_layout.mjs     optional phone-size check (needs Playwright)
```

To preview the example yourself:

```bash
python scripts/build.py assets/example-data.json example.html
```

Open `example.html` in a browser. Tap or click the right side (or press →) to go forward, the left side (or ←) to go back. It follows your system's light or dark mode and respects reduced motion.
