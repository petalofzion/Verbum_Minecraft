# Clean Room Logs

This directory is intended for "Clean Room Design" documentation. When implementing a feature or mechanism that is inspired by, or functionally equivalent to, an existing external project, but which needs to be developed without direct exposure to the external project's source code, document the process here.

## Purpose:

*   **Legal Protection:** Provides a verifiable paper trail demonstrating independent development, mitigating claims of copyright infringement or intellectual property misuse.
*   **Architectural Purity:** Ensures that external implementations do not inadvertently influence the internal design beyond the high-level functional specification.
*   **Transparency:** Offers insight into design decisions and the thought process behind specific implementations.

## Guidelines:

1.  **Before Coding:** Write a design document outlining the mechanism or feature to be implemented. This document should *not* reference or be influenced by the external source code. Focus purely on the desired functionality and your proposed solution.
2.  **Date and Author:** Each log entry should be clearly dated and identify the author.
3.  **No Code References:** The design document should *not* contain snippets or direct references to the external codebase.
4.  **Functional Specification:** Describe the functionality, inputs, outputs, and any performance goals.
5.  **Review:** Ideally, have another developer review the design document *before* coding begins.

## Example Log Entry (File: `YYYY-MM-DD_FeatureName.md`):

```markdown
# Clean Room Log: Fast Energy Network Implementation (YYYY-MM-DD)

**Author:** [Your Name/Agent ID]

**Mechanism:** High-performance, batched energy transfer network between connected components.

**Desired Functionality:**
- Efficiently transfer energy between nodes in a grid.
- Minimize tick-time overhead.
- Support large networks with thousands of nodes.
- Energy flow should be directional (e.g., source to sink).

**Proposed Design:**
1. **Data Structure:** Represent the network as a sparse graph. Nodes (energy storage blocks) are vertices, and connections (pipes/cables) are edges.
2. **Tick Logic:** Instead of individual BlockEntities ticking, a central `sim-kernel` system will iterate over active network graphs.
3. **Batch Processing:** Each network graph will be processed once per tick. Energy transfer calculations will be batched.
4. **Energy Propagation:** Use a breadth-first or depth-first traversal to propagate energy requests/offers through the network, prioritizing paths of least resistance or highest demand.
5. **Data Locality:** Network data will be stored in flat arrays within the `sim-kernel` to maximize cache efficiency.

**Notes:** This design was developed after reviewing high-level concepts of energy systems in other Minecraft mods, but without direct examination of their source code.
```
