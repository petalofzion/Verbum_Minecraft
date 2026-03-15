# Verbum Idea Funnel

This is the chat-side path from vague inspiration to execution-ready packet.

Use it when an idea is still fuzzy and needs shape. The goal is not to force premature certainty. The goal is to move from intuition to clarity without losing the soul of the idea.

---

## Stage 1 — Spark

### What can enter here
Almost anything:

- a sentence
- a mechanic hunch
- a mood or image
- a title
- a profile guess
- a book/manual concept
- a system complaint
- a “wouldn't it be lovely if...” fragment
- a repair impulse like “this profile still feels thin”

### What matters here
Do **not** demand completeness.

At this stage, the only real job is to capture the spark honestly enough that it does not evaporate.

### Good outputs
- a rough title
- a one-sentence desire
- a tentative profile guess
- a note about what feels missing or attractive

---

## Stage 2 — Distill

Now the chat should turn the spark into a cleaner creative shape.

### Resolve these first
- **player fantasy** — what does the player feel, do, or notice?
- **player-facing purpose** — why should this exist in play?
- **owning profile** — where does it belong?
- **dominant weather** — cathedral realism or apocalyptic mythic?
- **progression role** — early, mid, late, optional, systemic, decorative, pressure layer?
- **non-goals** — what should it explicitly not become?

### Good questions
- what is the center of gravity here?
- what would make this feel complete in a small version?
- what kind of mistake would overinflate this idea?

### Rule
Do **not** jump to code structure yet.

---

## Stage 3 — Repo Translation

Once the idea has a stable creative center, translate it into repo implications.

### Resolve these next
- **packet type** — `feature | bugfix | refactor | spike | content`
- **likely touched repo areas**
- **capsule-local or repo-agent scope**
- **does it change repo-level seams?**
- **likely update surfaces**
- **verification burden**

### Plain translation
This stage asks: what kind of work is this, and how dangerous is it?

A content-only manual update is not the same species of task as a new cross-module gameplay seam.

---

## Stage 4 — Packetization

Turn the idea into one or more execution artifacts:

- feature intake
- decision ledger
- orchestrator packet
- verifier packet when needed

At this point, the idea should be clear enough that a repo orchestrator can own the loop without constant supervision.

---

## Heuristics That Usually Help

- prefer one clean feature over three half-related mechanics
- decide profile ownership before debating implementation details
- separate fantasy from implementation
- separate product meaning from wiring implications
- split seam work from capsule work when they have different risk levels
- write non-goals early; they save a ridiculous amount of thrashing later
- when in doubt, make the first pass smaller and clearer

---

## Common Failure Modes

### Vague beauty, no action
The idea sounds gorgeous but no one can say what changes for the player.

### Ownership drift
Everyone keeps talking as though the profile is obvious, but nobody has actually named it.

### Visions inflation
The idea becomes bigger and shinier every time it is discussed, whether or not that helps it.

### False urgency toward code
The conversation jumps to architecture before the feature's fantasy is even stable.

### Hidden non-goals
People only state what they want, not what they refuse. This creates packet bloat.

### Seam confusion
A simple capsule task gets framed like a repo-seam project, or a seam-heavy task gets underestimated as “just content.”

---

## Worked Example

### Stage 1 — Spark
"Wouldn't it be lovely if Vocations had a kitchen-garden guide that made domestic care feel like actual play, not just vibes?"

### Stage 2 — Distill
- **fantasy:** the player tends a small domestic growing loop that feels rooted and useful
- **purpose:** give Vocations a lived-in household rhythm
- **profile:** Vocations
- **weather:** cathedral realism
- **progression role:** early calm loop / orientation into profile identity
- **non-goals:** not a giant farming overhaul, not a questline, not combat, not broad magic overlap

### Stage 3 — Repo Translation
- **packet type:** probably `feature`
- **scope:** likely capsule-local unless new contracts appear
- **update surfaces:** capsule index, module metadata if new capsule, TODO surfaces, manuals if player-facing guidance is added
- **verification burden:** normal build + profile placement sanity + capsule boundary checks

### Stage 4 — Packetization
Now the idea is ready to become a feature intake, decision ledger, and orchestrator packet.

---

## When to Split Seam Work from Capsule Work

Split the task when the answer to any of these is “yes”:

- does this require a new long-lived API/SPI contract?
- does this change assembly wiring in a meaningful way?
- does this introduce schema/save compatibility risk?
- would one worker be blocked waiting on a repo-level seam anyway?

### Typical pattern
1. seam packet
2. seam verification
3. capsule packet
4. final integration

If none of those are true, keep it simple and avoid inventing ceremony.

---

## Ready for a Packet When...

- the core fantasy is clear
- profile ownership is at least mostly clear
- dominant weather is named
- non-goals are stated
- likely repo impact is understood
- verification burden is acknowledged
- the conversation can describe a small successful first version

If those are true, the idea is usually ready enough.

---

## Related Docs

- `./CHAT_PRIMER.md`
- `./PROFILE_ATLAS.md`
- `./PACKET_WORKFLOW.md`
- `./ORCHESTRATOR_PACKET_TEMPLATE.md`

