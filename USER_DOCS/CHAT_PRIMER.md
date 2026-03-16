# Verbum Chat Primer

This is the front-door guide for ideation chats about Verbum.

Use it when an idea is still soft, half-formed, intuitive, or only present as a mood, image, mechanic, title, or complaint. Its job is to help a human or chat partner turn that spark into something clear enough to become a packet for repo execution.

This is a creative-and-operational guide. It is not the repo's deepest source of architectural law.

---

## Why Verbum Exists

Verbum is trying to do something unusual on purpose.

It wants the breadth of a huge modded Minecraft experience without the usual modpack glue, duplication, tonal collision, and systems spaghetti. It aims for one world with one internal language: one taxonomy, one schema, one simulation contract, and one player-facing design grammar.

Its hidden thread is Christ-centered orientation, but mostly by structure rather than slogans: rhythm, return, stewardship, hospitality, memory, thresholds, architecture, care, and intelligibility. The point is not to paste sermons onto systems. The point is to make the world feel quietly ordered.

If a player never thinks about theology, Verbum should still feel coherent, beautiful, humane, and deeply intentional.

---

## What Verbum Is

- a single cohesive Minecraft project
- a modular monolith with one world-logic and one design language
- a large-scale experience built through coherence rather than pile-on accumulation
- a world where practical guidance, manuals, and orientation texts matter
- a project that treats beauty, clarity, and continuity as gameplay-adjacent virtues

## What Verbum Is Not

- not a random bucket of unrelated mods
- not generic fantasy with church paint on top
- not a sermon machine
- not a coercive devotional system
- not four profiles mashed into one mushy identity
- not a place where every cool idea belongs merely because it is cool

---

## Creative Constitution

Keep these close. They are the shortest useful summary of Verbum's taste.

1. **Coherence before accumulation.**
   A smaller, cleaner idea is usually better than three adjacent half-ideas.
2. **Quiet sacredness before loud signaling.**
   Suggestion, architecture, rhythm, and naming usually beat constant explicit declaration.
3. **Practical beauty before ornamental excess.**
   Let things be lovely, but also legible, usable, and materially grounded.
4. **Profile distinction before feature sprawl.**
   Each profile should feel like itself.
5. **Manuals before lore when clarity matters.**
   Verbum often teaches through field texts, handbooks, atlases, rules, and devotional guides.
6. **Depth through return, not just novelty.**
   Good systems reward attention, revisiting, stewardship, and learning.
7. **Breadth without taxonomy fracture.**
   The world should widen without becoming internally inconsistent.

---

## Aesthetic Spine

Verbum should feel like:

- quiet sacredness
- architecture, rhythm, return, and care
- human, earthy, worn, beautiful, intelligible design
- stewardship, memory, craft, and practical wonder
- systems that cohere instead of merely accumulate

A good Verbum idea often feels as though it could belong in a world of:

- stone, timber, dust, vellum, ink, candlelight, gardens, bells, gates, roads, fields, ash, roots, thresholds, stars, and weathered tools

Use those as seasoning, not as a mandatory checklist.

---

## Two Spiritual Weathers

These are the quickest tonal compass available in ideation chats.

### Cathedral Realism
Grounded, pastoral, domestic, practical, historical, human-scale, worn, and steady.

Good for:
- baseline systems
- household or workshop life
- farming and craft
- manuals and orientation texts
- anything that should feel inhabitable first and wondrous second

### Apocalyptic Mythic
Luminous, symbolic, visionary, uncanny, charged with signs, strange order, and layered meaning.

Good for:
- large exploration arcs
- magic and mystery
- thresholds, ruins, revelation, pilgrimage, prophecy-shaped content
- systems that should feel expansive or numinous

An idea can mix them, but one weather should usually dominate.

---

## The Four Live Profiles

These are the live player-facing lines of Verbum. For full texture, use `PROFILE_ATLAS.md`.

### Veritas
Refined baseline. Restrained, trustworthy, foundational, legible.

### Vocations
Warm domestic expansion. Work, craft, stewardship, building, farming, local life, and practical beauty.

### Visions
Broad flagship line. Exploration, wonder, tech, magic, layered progression, larger systems, luminous breadth.

### Vorago
Pressure layer above Visions. Scarcity, attrition, exposure, discipline, punitive survival law; not juvenile grimdark sludge.

### Upgrade Rule
Profiles inherit upward:

`Veritas -> Vocations -> Visions -> Vorago`

That means profile choice is not only a mood question. It also affects where things belong and how they travel upward.

---

## Architecture in Plain Language

Ideation chats do not need every architectural detail, but they do need the right instincts.

- Verbum is a **tiered modular monolith**, not a grab-bag.
- Feature modules are mostly about content, registration, and bounded feature logic.
- Cross-feature communication should go through **API/SPI**, not direct feature-to-feature tangles.
- **Assemblies** are the layer that touches Fabric/Minecraft wiring and config/IO.
- The repo is trying to preserve one taxonomy, one schema, one simulation contract, and one UX language.

Plain translation: when you and the chat are shaping an idea, you do not need to design every class. But you *do* need to be aware of whether the idea is:

- content-only
- capsule-local implementation
- cross-module seam work
- assembly / profile wiring work

That distinction matters later when the packet is built.

---

## How to Use This Primer in a Real Chat

When you bring an idea here, you do **not** need to arrive with a polished feature spec.

A good starting point can be:

- a title
- a mechanic hunch
- a mood
- a complaint about what is missing
- an image like “a book that teaches winter discipline”
- a sentence like “I want Visions to feel more like learned pilgrimage than pure power fantasy”

From there, the chat should help you do five things:

1. name the player fantasy
2. identify likely profile ownership
3. identify dominant weather
4. separate must-haves from non-goals
5. translate the idea into something packet-ready

The goal is not to make everything technical too early. The goal is to make it *clear*.

---

## Discussion Principles for Good Verbum Chats

### Start with fantasy, not implementation
Ask first: what should the player feel, notice, do, or return to?

### Decide ownership early
Many bad conversations come from talking about implementation before deciding whether the idea belongs to Veritas, Vocations, Visions, or Vorago.

### Name the non-goals
This is one of the fastest ways to prevent feature sprawl.

### Keep practical guidance first-class
A book, manual, chart, devotional, field text, or handbook is often a real design surface in Verbum, not decorative fluff.

### Prefer one clean center of gravity
If an idea seems to belong equally to all profiles and all systems, it is probably still too vague.

### Let beauty stay legible
Pretty language is welcome. Vagueness is not.

---

## Common Drift Patterns

Watch for these little gremlins.

### “This is lovely” but has no play purpose
The idea sounds beautiful, but does not change how the player learns, acts, returns, survives, travels, or understands the world.

### Visions eats everything
A lot of ideas are expansive and interesting. That does not automatically make them Visions. Sometimes the true home is Vocations or even Veritas.

### Vorago becomes edgy sludge
Vorago should feel severe, weathered, and disciplined — not cartoonishly cruel or nihilistic.

### Devotion becomes a buff vending machine
Prayer, charity, ritual, or spiritual posture should not collapse into “press button, receive stat bonus” unless the design is unusually careful.

### Christian explicitness overwhelms usability
If the player-facing text stops helping the player and starts merely signaling, pull it back.

### Beauty replaces clarity
If the prose is atmospheric but nobody can tell what the thing does, rewrite it.

---

## Worked Mini-Example

### Raw spark
“I want a little winter-facing book or ritual thing that makes Vocations feel more seasonal and home-like.”

### Distillation
- **Fantasy:** the player prepares for winter with domestic attention rather than panic.
- **Purpose:** give Vocations a stronger sense of household rhythm and seasonal care.
- **Likely profile:** Vocations.
- **Weather:** Cathedral realism.
- **Possible form:** content-first manual/book, maybe later a feature.
- **Non-goals:** not a survival-horror freeze system, not a giant farming overhaul, not a prayer buff machine.

### Repo translation
- likely packet type: `content` first, possibly `feature` later
- likely scope: capsule-local library/manual update
- likely update surfaces: player-facing manuals, capsule index if purpose summary changes, maybe TODO surfaces
- likely verification burden: content/resource integrity + normal build

### Packet-ready version
“Expand the Vocations manual layer with a winter household guide that teaches seasonal preparedness, domestic rhythms, and practical care. Keep it useful, warm, and grounded. No new mechanics in this first pass.”

That is the kind of move we want: from soft intuition to clean intent.

---

## Quick Intake Block

Use this at the start of a chat when you want to move quickly.

```md
I have an idea for:
<name or rough concept>

What kind of thing is it?
<feature | content | mechanic | profile book | refactor | vibe/world idea>

What do I want the player to feel or do?
<one sentence>

Which profile feels most likely?
<veritas | vocations | visions | vorago | unsure>

Which weather fits best?
<cathedral realism | apocalyptic mythic | mixed | unsure>

What is definitely not the goal?
<one or two lines>

How formed is this?
<tiny spark | rough concept | half-designed | nearly packet-ready>
```

---

## Related Docs

- `./PROFILE_ATLAS.md`
- `./IDEA_FUNNEL.md`
- `./PACKET_WORKFLOW.md`
- `./ORCHESTRATOR_PACKET_TEMPLATE.md`

