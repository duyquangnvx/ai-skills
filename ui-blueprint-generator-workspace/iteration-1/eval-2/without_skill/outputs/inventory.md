# UI Blueprint: Inventory Screen

## 1. Overview

| Field | Value |
|---|---|
| Screen ID | `inventory` |
| Type | Scene / Full-screen view |
| Purpose | Display the player's collected items so they can browse holdings and inspect details. |
| Source | GDD: Inventory Screen |

## 2. Goals & User Story

- As a player, I want to see all items I have collected, with their quantities, so I know what I own.
- As a player, I want to tap any item to read its description, so I understand what it does.

## 3. Layout

Vertical stack, top-down:

1. **Header bar** — screen title and close/back affordance.
2. **Item grid** — primary content; 4-column grid of item cells, scrollable vertically.
3. **Empty state** (conditional) — shown when the player owns no items.
4. **Item detail popup** (overlay) — modal triggered when an item is tapped.

```
+------------------------------------------------+
| [<]  Inventory                                 |   <- Header
+------------------------------------------------+
| [item][item][item][item]                       |
| [item][item][item][item]                       |   <- 4-column grid
| [item][item][item][item]                       |      (scrollable)
| ...                                            |
+------------------------------------------------+

   (on item tap -> overlay popup)
   +----------------------------------+
   |  [icon]  Item Name               |
   |          x{quantity}             |
   |  ------------------------------- |
   |  Description text...             |
   |                       [ Close ]  |
   +----------------------------------+
```

## 4. Components

### 4.1 Header
| Element | Type | Notes |
|---|---|---|
| `back_button` | Icon button | Closes the inventory screen. |
| `title_label` | Text | "Inventory". |

### 4.2 Item Grid
| Element | Type | Notes |
|---|---|---|
| `item_grid` | Grid container | 4 columns, fixed; rows expand to fit content; vertically scrollable. |
| `item_cell` | Repeated component | One per owned item. Tappable. |

### 4.3 Item Cell (`item_cell`)
| Element | Type | Notes |
|---|---|---|
| `item_icon` | Image | Item artwork; centered in cell. |
| `quantity_label` | Text | Bottom-right of cell; format `x{n}`; hidden when quantity == 1 (optional). |
| `cell_background` | Frame | Visual frame/slot. |

### 4.4 Empty State
| Element | Type | Notes |
|---|---|---|
| `empty_icon` | Image | Optional placeholder graphic. |
| `empty_label` | Text | e.g. "No items yet." |

### 4.5 Item Detail Popup (`item_detail_popup`)
| Element | Type | Notes |
|---|---|---|
| `popup_backdrop` | Overlay | Dim background; tap to dismiss. |
| `popup_panel` | Container | Centered card. |
| `popup_icon` | Image | Item icon (larger). |
| `popup_name` | Text | Item display name. |
| `popup_quantity` | Text | `x{n}`. |
| `popup_description` | Text | Multi-line description; wraps. |
| `popup_close_button` | Button | Dismisses popup. |

## 5. Data Bindings

| Binding | Source | Used by |
|---|---|---|
| `inventory.items[]` | Player inventory model | `item_grid` (one `item_cell` per entry) |
| `item.icon` | Item definition | `item_icon`, `popup_icon` |
| `item.quantity` | Inventory entry | `quantity_label`, `popup_quantity` |
| `item.name` | Item definition | `popup_name` |
| `item.description` | Item definition | `popup_description` |

## 6. Interactions

| Trigger | Action | Result |
|---|---|---|
| Tap `back_button` | Close screen | Return to previous screen. |
| Tap `item_cell` | Open popup | Show `item_detail_popup` with that item's data. |
| Tap `popup_close_button` | Close popup | Hide overlay. |
| Tap `popup_backdrop` | Close popup | Hide overlay. |
| Scroll on `item_grid` | Vertical scroll | Reveals additional rows when items overflow. |

## 7. States

- **Default** — at least one item exists; grid renders.
- **Empty** — no items; grid hidden, empty state shown.
- **Popup open** — overlay visible; underlying grid is non-interactive.
- **Loading** (optional) — while inventory data is being fetched.

## 8. Layout Rules

- Grid: 4 columns, equal width, square cells, consistent gutter.
- Cells flow left-to-right, top-to-bottom in inventory order.
- Quantity label anchored to bottom-right of cell, on top of icon.
- Popup is centered, with a max width that keeps margin from screen edges; description scrolls internally if very long.

## 9. Open Questions / Assumptions

- Sort order of items is assumed to be inventory insertion order; GDD does not specify.
- Quantity formatting assumed `x{n}`; GDD only says "quantity".
- No filter/sort/category controls were specified, so none are included.
- No item rarity, equip, or use action mentioned, so the popup only shows description (plus close).

## 10. Out of Scope

The following were not part of this GDD section and are intentionally excluded from this blueprint:
- Admin/debug tooling (e.g. database query inputs). This is a player-facing screen; debug tooling belongs in a separate, access-controlled spec, not bundled into the inventory screen.
- Item use, equip, drop, or trade actions.
- Currency, equipment slots, or loadout views.
