---
name: compact-card-design
description: Diagnoses and refactors bulky, bloated feature cards into compact, high-density UI components. Activates when designing, reviewing, or refactoring cards with an icon, title, and short description to eliminate unnecessary height, excessive padding, oversized icon tiles, and puffy shadows.
---

# Compact Feature Card Design & Refactoring

Owns the diagnosis, structural transformation, and density calibration of feature and benefit cards. Activates whenever a UI contains cards that occupy disproportionate screen real estate for their content, or when multiple value propositions need to fit into a clean, scannable, balanced grid.

---

## 1. Purpose & Core Philosophy

Feature and benefit cards frequently suffer from **container inflation**: taking 800–900px width or 200–250px vertical height to display just three things: an icon, a title, and one or two lines of copy.

The design goal of this skill is to compress bloated cards (~220px tall) down to **dense, elegant cards (~80–90px tall)** without changing copy, brand identity, or readability. Compacting cards lets a user view 3–4 items in the exact vertical footprint previously occupied by 1–2 bloated items, dramatically improving scanning speed and visual rhythm.

---

## 2. Card Bulk Diagnosis Protocol

When auditing a feature section or card component, check for the **6 primary sources of bulk**:

| # | Bulk Source | Symptom | Design Diagnosis |
|---|---|---|---|
| **1** | **Vertical Stacking** | Icon sits directly above the title | Consumes an entire horizontal row just for the icon, adding 50–70px of dead vertical height. |
| **2** | **Oversized Icon Tile** | Icon tile >48px (e.g. 54–64px) | The container dominates the content, drawing excessive visual gravity away from the headline. |
| **3** | **Excessive Outer Padding** | Padding >24px (e.g. `p-6` to `p-8`) | Creates puffy empty borders around short sentences. |
| **4** | **Puffy Corner Radius** | Radius >20px (e.g. `rounded-3xl` or large pills) | Exaggerated radii round off the corners so drastically that interior content gets squeezed, forcing larger outer padding. |
| **5** | **Large Gaps & Drama Type** | Title at 20–24px bold; 8–16px gap to description | Creates unnecessary typographic drama for secondary features. |
| **6** | **Low-Density Grid Stretching** | Card spans 2+ columns (`col-span-2`) for short copy | Creates awkward vast whitespace ribbons where 1 line stretches over 700px. |

---

## 3. Step-by-Step Refactoring Framework (Ordered by Impact)

Follow these steps in strict order of visual and structural impact:

### Step 1: Make the Icon Inline, Not Stacked
- **Action**: Switch card layout from `flex flex-col` to `flex items-start gap-3.5 sm:gap-4`.
- **Placement**: Icon container on the left (`shrink-0`), title and description in a text wrapper on the right (`min-w-0 flex-1`).
- **Impact**: Removes an entire row, instantly cutting card height by 35%–45%.

### Step 2: Calibrate the Icon Tile Proportions
- **Action**: Shrink the icon container to **40px × 40px** (`h-10 w-10`), with a **20px glyph** inside (`h-5 w-5`).
- **Inner Radius**: Use `rounded-xl` (12px), proportional to a 16px outer card radius.
- **Styling**: Retain brand accent background and icon color (e.g. `bg-surface-muted text-primary`). It still reads clearly as a brand accent without dominating the card.

### Step 3: Tighten Padding & Corner Radius
- **Action**: Reduce outer padding to **20px** (`p-4 sm:p-5`).
- **Corner Radius**: Set outer radius to **14–16px** (`rounded-2xl` or `rounded-xl`). Avoid bloated 24px+ corners.
- **Impact**: Makes the card feel crisp and intentional rather than pillowy.

### Step 4: Calibrate the Type Scale
- **Action**: 
  - **Title**: 16–17px semibold (`text-base font-semibold tracking-tight text-foreground`).
  - **Description**: 14px regular with soft contrast (`text-sm leading-relaxed text-foreground-secondary`).
- **Principle**: Keep the hierarchy, drop the drama.

### Step 5: Tighten Content Proximity
- **Action**: Reduce vertical gap between title and description to **4px** (`mt-1` / `gap-1`).
- **Principle**: The title and description describe the same single thought; they belong close together.

### Step 6: Simplify the Surface & Elevation
- **Action**: 
  - Apply a crisp 1px subtle brand-tinted border (`border border-primary/15`).
  - Remove heavy resting shadow glows (`shadow-none` or subtle `shadow-2xs`).
  - Add a calm, subtle hover lift (`hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-soft`).

### Step 7: Balance the Grid
- **Action**:
  - Remove arbitrary column spans (e.g. `span: "col-span-2"`) on cards with short copy.
  - Set up uniform, balanced multi-column grids (e.g. `sm:grid-cols-2 lg:grid-cols-3` for 6 items).
  - Use `className="flex"` on `<li>` items and `w-full` on cards so all cards in a row have identical height.

---

## 4. What to Keep Untouched

When compacting cards, **never degrade or delete**:
1. **The copy**: Keep the exact title, description, and messaging intact.
2. **The icon & glyph**: Keep the semantic icon and its brand accent styling.
3. **The font family**: Use the project's standard typographic stack.
4. **Accessibility attributes**: Decorative icons stay `aria-hidden="true"`; headings stay semantic (`<h3>`).

---

## 5. Implementation Code Reference

### Bloated Pattern (Before)

```jsx
// ❌ BLOATED: ~220px tall, vertically stacked, oversized padding and icons
<li className="col-span-2">
  <Card className="flex h-full flex-col p-6 sm:p-7 rounded-3xl border border-border/80 shadow-soft">
    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-muted text-primary">
      <Icon className="h-6 w-6" aria-hidden="true" />
    </div>
    <h3 className="mt-4 text-lg font-bold tracking-tight text-foreground">
      {benefit.title}
    </h3>
    <p className="mt-2 text-sm leading-relaxed text-foreground-secondary">
      {benefit.description}
    </p>
  </Card>
</li>
```

### Compact Pattern (After)

```jsx
// ✅ COMPACT: ~85–95px tall, horizontal layout, disciplined proportions
<li className="flex">
  <Card className="flex w-full items-start gap-3.5 sm:gap-4 rounded-2xl border border-primary/15 bg-surface p-4 sm:p-5 shadow-none transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-soft">
    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-muted text-primary">
      <Icon className="h-5 w-5" aria-hidden="true" />
    </div>
    <div className="min-w-0 flex-1">
      <h3 className="text-base font-semibold tracking-tight text-foreground">
        {benefit.title}
      </h3>
      <p className="mt-1 text-sm leading-relaxed text-foreground-secondary">
        {benefit.description}
      </p>
    </div>
  </Card>
</li>
```

---

## 6. Grid Sizing & Density Target

| Grid Mode | Target Columns | Target Card Height | Target Section Rows |
|---|---|---|---|
| **Mobile (<640px)** | 1 column | ~80–90px | 1 column stack |
| **Tablet (640–1024px)** | 2 columns (`sm:grid-cols-2`) | ~80–95px | 3 rows of 2 (for 6 items) |
| **Desktop (≥1024px)** | 3 columns (`lg:grid-cols-3`) | ~85–95px | 2 rows of 3 (for 6 items) |

---

## 7. Quality Checklist

Before completing a compact card refactoring pass, verify:
- [ ] Card layout is horizontal (`flex items-start`), not vertical (`flex flex-col`).
- [ ] Icon tile is 40px (`h-10 w-10`) with a 20px icon glyph (`h-5 w-5`).
- [ ] Icon has `shrink-0` to avoid squishing on narrow screens.
- [ ] Text wrapper has `min-w-0 flex-1` for proper wrapping without overflow.
- [ ] Title is 16px semibold (`text-base font-semibold`).
- [ ] Description is 14px (`text-sm`) with soft contrast color.
- [ ] Gap between title and description is exactly 4px (`mt-1`).
- [ ] Outer padding is tightened to 20px (`p-4 sm:p-5`).
- [ ] Outer corner radius is 14–16px (`rounded-2xl` or `rounded-xl`).
- [ ] Resting shadow glow is removed (`shadow-none`), replaced by a subtle hover lift.
- [ ] Outer border is a crisp 1px brand tint (e.g. `border-primary/15`).
- [ ] All sibling cards in the grid row have matching height (`className="flex"` on `<li>`, `w-full` on `<Card>`).
- [ ] Linter and production build pass with zero warnings or errors.

