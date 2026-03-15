package com.verbum_minecraft.features.library.librariansdesk;

import com.verbum_minecraft.api.content.BlockWorkstationHandler;
import com.verbum_minecraft.api.content.ItemGrant;
import com.verbum_minecraft.api.content.WorkstationActionRequest;
import com.verbum_minecraft.api.content.WorkstationActionResult;
import com.verbum_minecraft.api.content.WorkstationBookDraft;
import com.verbum_minecraft.api.content.WorkstationBookSnapshot;
import com.verbum_minecraft.api.content.WorkstationPlayerBookGrant;
import com.verbum_minecraft.api.content.WorkstationSlotDelta;
import com.verbum_minecraft.api.content.WorkstationSlotInput;
import com.verbum_minecraft.api.content.WorkstationUiSpec;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * Workstation rules for the Librarian's Desk.
 */
public final class LibrariansDeskWorkstationHandler implements BlockWorkstationHandler {
    private static final String BOOK_ID = "minecraft:book";
    private static final String WRITABLE_BOOK_ID = "minecraft:writable_book";
    private static final String WRITTEN_BOOK_ID = "minecraft:written_book";
    private static final String PAPER_ID = "minecraft:paper";
    private static final String LEATHER_ID = "minecraft:leather";
    private static final int DEFAULT_INPUT_SLOTS = 9;
    private static final int BOOK_PAPER_YIELD = 3;

    private static final Set<String> MANUAL_BOOK_IDS = Set.of(
        "verbum:bible",
        "verbum:book_of_hours",
        "verbum:dusty_devotional",
        "verbum:pilgrims_atlas",
        "verbum:rule_of_ashes"
    );

    @Override
    public WorkstationUiSpec uiSpec() {
        return new WorkstationUiSpec(
            DEFAULT_INPUT_SLOTS,
            true,
            true,
            true
        );
    }

    @Override
    public WorkstationActionResult apply(WorkstationActionRequest request) {
        String action = normalizedAction(request.actionId());
        if ("write_draft".equals(action)) {
            return applyDraftWrite(request);
        }
        if ("edit_player_book".equals(action)) {
            return applyPlayerBookEdit(request);
        }
        if ("copy_books".equals(action)) {
            return applyCopyMode(request);
        }
        if ("salvage_all".equals(action)) {
            return applySalvageMode(request);
        }
        return applyDefaultOpenMode(request);
    }

    private static WorkstationActionResult applyDraftWrite(WorkstationActionRequest request) {
        WorkstationBookDraft draft = request.draftBook();
        if (draft == null) {
            return WorkstationActionResult.handled(
                List.of(),
                List.of(),
                List.of(),
                "No draft content was provided."
            );
        }

        WorkstationSlotInput source = firstMatchingSlot(request.inputSlots(), slot ->
            BOOK_ID.equals(slot.itemId()) || WRITABLE_BOOK_ID.equals(slot.itemId())
        );
        if (source == null) {
            return WorkstationActionResult.handled(
                List.of(),
                List.of(),
                List.of(),
                "Insert a book or book-and-quill source to write a draft."
            );
        }

        WorkstationPlayerBookGrant written = new WorkstationPlayerBookGrant(draft.title(), draft.pages());
        return WorkstationActionResult.handled(
            List.of(new WorkstationSlotDelta(source.slotIndex(), 1)),
            List.of(),
            List.of(written),
            "Draft written as a player-owned book."
        );
    }

    private static WorkstationActionResult applyPlayerBookEdit(WorkstationActionRequest request) {
        List<WorkstationSlotDelta> deltas = new ArrayList<>();
        List<ItemGrant> grants = new ArrayList<>();

        for (WorkstationSlotInput slot : request.inputSlots()) {
            if (!WRITTEN_BOOK_ID.equals(slot.itemId())) {
                continue;
            }
            if (slot.book() == null) {
                continue;
            }
            deltas.add(new WorkstationSlotDelta(slot.slotIndex(), slot.count()));
            grants.add(new ItemGrant(WRITABLE_BOOK_ID, slot.count()));
        }

        if (deltas.isEmpty()) {
            return WorkstationActionResult.handled(
                List.of(),
                List.of(),
                List.of(),
                "Insert player-written books to convert into editable drafts."
            );
        }
        return WorkstationActionResult.handled(
            deltas,
            grants,
            List.of(),
            "Converted player books into editable drafts."
        );
    }

    private static WorkstationActionResult applyCopyMode(WorkstationActionRequest request) {
        int sourceCopiesRequested = 0;
        for (WorkstationSlotInput slot : request.inputSlots()) {
            if (isCopyCandidate(slot)) {
                sourceCopiesRequested += slot.count();
            }
        }
        if (sourceCopiesRequested <= 0) {
            return WorkstationActionResult.handled(
                List.of(),
                List.of(),
                List.of(),
                "Insert Verbum manuals or player-written books to copy."
            );
        }

        int blankBooksAvailable = totalCountForItem(request.inputSlots(), BOOK_ID);
        if (blankBooksAvailable <= 0) {
            return WorkstationActionResult.handled(
                List.of(),
                List.of(),
                List.of(),
                "Insert plain books as copy targets."
            );
        }

        int copiesToProduce = Math.min(sourceCopiesRequested, blankBooksAvailable);
        List<WorkstationPlayerBookGrant> copies = new ArrayList<>(copiesToProduce);
        for (WorkstationSlotInput slot : request.inputSlots()) {
            if (!isCopyCandidate(slot)) {
                continue;
            }
            for (int i = 0; i < slot.count() && copies.size() < copiesToProduce; i++) {
                copies.add(copyFromSlot(slot));
            }
            if (copies.size() >= copiesToProduce) {
                break;
            }
        }

        List<WorkstationSlotDelta> deltas = consumeFromItemSlots(
            request.inputSlots(),
            BOOK_ID,
            copiesToProduce
        );

        String message = copiesToProduce < sourceCopiesRequested
            ? "Copied " + copiesToProduce + " books. Add more plain books to copy the rest."
            : "Copied books into player-owned written copies.";
        return WorkstationActionResult.handled(
            deltas,
            List.of(),
            copies,
            message
        );
    }

    private static WorkstationActionResult applySalvageMode(WorkstationActionRequest request) {
        List<WorkstationSlotDelta> deltas = new ArrayList<>();
        List<ItemGrant> grants = collapseGrants(collectSalvageGrants(request.inputSlots(), deltas));
        if (deltas.isEmpty()) {
            return WorkstationActionResult.handled(
                List.of(),
                List.of(),
                List.of(),
                "Insert books to salvage into materials."
            );
        }
        return WorkstationActionResult.handled(
            deltas,
            grants,
            List.of(),
            "Recovered binding materials from books."
        );
    }

    private static WorkstationActionResult applyDefaultOpenMode(WorkstationActionRequest request) {
        if (!hasBookLikeInputs(request.inputSlots())) {
            return WorkstationActionResult.pass();
        }
        return WorkstationActionResult.handled(
            List.of(),
            List.of(),
            List.of(),
            "Choose an action: Salvage, Copy, Edit, or Write."
        );
    }

    private static List<ItemGrant> collectSalvageGrants(
        List<WorkstationSlotInput> slots,
        List<WorkstationSlotDelta> deltas
    ) {
        List<ItemGrant> grants = new ArrayList<>();
        for (WorkstationSlotInput slot : slots) {
            String itemId = slot.itemId();
            if (BOOK_ID.equals(itemId)) {
                deltas.add(new WorkstationSlotDelta(slot.slotIndex(), slot.count()));
                grants.add(new ItemGrant(PAPER_ID, BOOK_PAPER_YIELD * slot.count()));
                grants.add(new ItemGrant(LEATHER_ID, slot.count()));
                continue;
            }
            if (WRITABLE_BOOK_ID.equals(itemId) || WRITTEN_BOOK_ID.equals(itemId) || MANUAL_BOOK_IDS.contains(itemId)) {
                deltas.add(new WorkstationSlotDelta(slot.slotIndex(), slot.count()));
                grants.add(new ItemGrant(PAPER_ID, BOOK_PAPER_YIELD * slot.count()));
            }
        }
        return grants;
    }

    private static WorkstationPlayerBookGrant copyFromSlot(WorkstationSlotInput slot) {
        WorkstationBookSnapshot snapshot = slot.book();
        if (snapshot != null) {
            String title = fallbackTitle(snapshot.title(), slot.itemId());
            List<String> pages = snapshot.pages().isEmpty()
                ? List.of("Copied from " + title + ".")
                : snapshot.pages();
            return new WorkstationPlayerBookGrant(title, pages);
        }
        String title = fallbackTitle(null, slot.itemId());
        return new WorkstationPlayerBookGrant(title, List.of("Copied from " + title + "."));
    }

    private static String fallbackTitle(String title, String itemId) {
        if (title != null && !title.isBlank()) {
            return title;
        }
        String path = itemId;
        int separator = itemId.indexOf(':');
        if (separator >= 0 && separator < itemId.length() - 1) {
            path = itemId.substring(separator + 1);
        }
        String[] words = path.split("_");
        StringBuilder builder = new StringBuilder();
        for (String word : words) {
            if (word.isBlank()) {
                continue;
            }
            if (!builder.isEmpty()) {
                builder.append(' ');
            }
            builder.append(word.substring(0, 1).toUpperCase(Locale.ROOT))
                .append(word.substring(1));
        }
        if (builder.isEmpty()) {
            return "Copied Book";
        }
        return builder.toString();
    }

    private static boolean isCopyCandidate(WorkstationSlotInput slot) {
        return MANUAL_BOOK_IDS.contains(slot.itemId()) || (WRITTEN_BOOK_ID.equals(slot.itemId()) && slot.book() != null);
    }

    private static int totalCountForItem(List<WorkstationSlotInput> slots, String itemId) {
        int total = 0;
        for (WorkstationSlotInput slot : slots) {
            if (itemId.equals(slot.itemId())) {
                total += slot.count();
            }
        }
        return total;
    }

    private static List<WorkstationSlotDelta> consumeFromItemSlots(
        List<WorkstationSlotInput> slots,
        String itemId,
        int amount
    ) {
        List<WorkstationSlotDelta> deltas = new ArrayList<>();
        int remaining = amount;
        for (WorkstationSlotInput slot : slots) {
            if (remaining <= 0) {
                break;
            }
            if (!itemId.equals(slot.itemId()) || slot.count() <= 0) {
                continue;
            }
            int consume = Math.min(slot.count(), remaining);
            deltas.add(new WorkstationSlotDelta(slot.slotIndex(), consume));
            remaining -= consume;
        }
        return deltas;
    }

    private static WorkstationSlotInput firstMatchingSlot(
        List<WorkstationSlotInput> slots,
        SlotMatcher matcher
    ) {
        for (WorkstationSlotInput slot : slots) {
            if (matcher.matches(slot)) {
                return slot;
            }
        }
        return null;
    }

    private static boolean isBookLike(String itemId) {
        return BOOK_ID.equals(itemId)
            || WRITABLE_BOOK_ID.equals(itemId)
            || WRITTEN_BOOK_ID.equals(itemId)
            || MANUAL_BOOK_IDS.contains(itemId);
    }

    private static boolean hasBookLikeInputs(List<WorkstationSlotInput> slots) {
        for (WorkstationSlotInput slot : slots) {
            if (isBookLike(slot.itemId()) && slot.count() > 0) {
                return true;
            }
        }
        return false;
    }

    private static String normalizedAction(String actionId) {
        if (actionId == null || actionId.isBlank()) {
            return "open";
        }
        return actionId.trim().toLowerCase(Locale.ROOT);
    }

    private static List<ItemGrant> collapseGrants(List<ItemGrant> grants) {
        Map<String, Integer> totals = new LinkedHashMap<>();
        for (ItemGrant grant : grants) {
            totals.merge(grant.itemId(), grant.count(), Integer::sum);
        }
        List<ItemGrant> collapsed = new ArrayList<>(totals.size());
        for (Map.Entry<String, Integer> entry : totals.entrySet()) {
            collapsed.add(new ItemGrant(entry.getKey(), entry.getValue()));
        }
        return collapsed;
    }

    @FunctionalInterface
    private interface SlotMatcher {
        boolean matches(WorkstationSlotInput slot);
    }
}
