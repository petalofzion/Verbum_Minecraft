# Verbum Packet Workflow

This is the short map from chat ideation to repo execution.

Its purpose is simple: help a human or chat partner decide what kind of packet to create, what level of repo authority is needed, and what kind of verification should follow.

---

## The Main Flow

1. **Idea spark**
2. **Concept distillation**
3. **Decision ledger**
4. **Packet selection**
5. **Repo execution**
6. **Verification**
7. **Review and refine**

This is the normal path. The main decision point is not whether to use a packet. It is **which kind of packet and which lane of execution** the idea needs.

---

## The Three Main Lanes

## 1) Content-only lane
Use this when the task is mostly:

- books
- manuals
- naming
- profile guidance
- player-facing copy
- lore-adjacent content that should still be useful

### Typical flow
1. shape the idea in chat
2. create a `content` packet
3. run repo execution
4. verify resource/content integrity + build
5. review tone, usefulness, and profile distinction

### Typical repo impact
- capsule-local content files
- player-facing docs/manuals
- capsule index or TODO surfaces if summaries move

---

## 2) Capsule-local feature lane
Use this when the task is a real implementation, but mostly inside one bounded feature or a couple of tightly related capsules.

### Typical flow
1. shape the feature in chat
2. create a `feature` packet
3. let the orchestrator spawn bounded capsule workers if helpful
4. integrate and verify
5. review profile placement and update surfaces

### Typical repo impact
- one or a few feature capsules
- module metadata if a new capsule/module is added
- player-facing content tied to the feature
- capsule index / TODO / tests

---

## 3) Repo-seam lane
Use this when the task changes shared seams or carries real architectural risk.

### Common signs
- new API/SPI contract
- assembly wiring change
- save/schema compatibility risk
- profile/edition propagation risk
- verifier gate clearly needed before capsule work continues

### Typical flow
1. shape the idea in chat
2. create a seam-aware packet or separate seam packet
3. implement and verify the seam first
4. then implement dependent capsule work
5. run final integration and verification

### Rule of thumb
If seam work and capsule work have different risk profiles, split them. Do not make one packet do six jobs poorly.

---

## Decision Ledger Questions

Before choosing a packet lane, answer these:

- what is the player fantasy?
- what profile owns this?
- what weather dominates?
- what kind of packet is this?
- is it capsule-local or repo-agent scope?
- does it create or change repo-level seams?
- what update surfaces will change?
- what verification is the real floor, not the pretend floor?

Those questions usually tell you which lane to use.

---

## Artifact Set

The normal artifact ladder is:

1. **feature intake**
2. **decision ledger**
3. **orchestrator packet**
4. **verifier packet** when needed

### In plain language
- the **feature intake** holds the design heart
- the **decision ledger** compresses ambiguity
- the **orchestrator packet** tells the repo agent what it is allowed to do
- the **verifier packet** exists when a seam or risk surface needs explicit gatekeeping

---

## Review Loop

After repo execution, always review three things:

### 1. Did the implementation match the fantasy?
Not just “did it compile?” but “did it become the right thing?”

### 2. Did profile ownership stay clean?
A mechanically fine feature can still feel like it belongs to the wrong profile.

### 3. Were the repo's memory surfaces refreshed?
Check update targets, docs, indexes, metadata, and any required verification surfaces.

This is how you stop the repo from becoming technically correct and spiritually messy.

---

## Fast Rule of Thumb

- use **chat docs** to shape the idea
- use **repo docs** to execute the idea
- keep the packet concrete
- keep verification explicit
- split seam work from capsule work when needed
- do not let packet scope swell just because the idea is exciting

---

## Related Docs

- `./CHAT_PRIMER.md`
- `./PROFILE_ATLAS.md`
- `./IDEA_FUNNEL.md`
- `./ORCHESTRATOR_PACKET_TEMPLATE.md`
- `./FEATURE_PACKET_EXAMPLE.md`
- `./CONTENT_PACKET_EXAMPLE.md`

