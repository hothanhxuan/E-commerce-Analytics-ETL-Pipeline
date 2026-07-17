# 📊 Power BI Score Card Layout Guide — TechStore Vietnam

## Overview

Each of the 3 dashboard pages has a **top row of 5 score cards** using the **Card (new)** visual.
All cards follow the same dark theme from `TechStore_theme.json`.

---

## Card Layout (All Pages)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Page Canvas (1280 × 720 px, Background: #1A2332)                          │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Card 1  │  │  Card 2  │  │  Card 3  │  │  Card 4  │  │  Card 5  │     │
│  │          │  │          │  │          │  │          │  │          │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│  ← 20px margin →                                   ← 20px margin →        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │                   Remaining chart area                              │    │
│  │                   (y = 150px onward)                                │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exact Card Positioning (pixels)

| Card # | X Position | Y Position | Width | Height |
|--------|-----------|-----------|-------|--------|
| Card 1 | 20        | 20        | 230   | 110    |
| Card 2 | 268       | 20        | 230   | 110    |
| Card 3 | 516       | 20        | 230   | 110    |
| Card 4 | 764       | 20        | 230   | 110    |
| Card 5 | 1012      | 20        | 230   | 110    |

> **Spacing:** 18px gap between cards, 20px margin from page edges, 20px top margin.

---

## Card Visual Settings (Apply to ALL Cards)

### In Power BI Desktop:
1. Use **Card (new)** visual (not the legacy Card)
2. Apply these Format settings:

| Property | Setting |
|----------|---------|
| **Callout Value** | |
| → Font | Segoe UI Semibold |
| → Size | 28 pt |
| → Color | `#ECF0F1` (White) |
| **Category Label** | |
| → Font | Segoe UI |
| → Size | 10 pt |
| → Color | `#95A5A6` (Gray) |
| **Card Background** | `#243447` |
| **Border** | |
| → Color | `#3498DB` (Accent Blue) |
| → Radius | 8 px |
| → Width | 1 px |
| **Shadow** | Off |
| **Padding** | 12 px all sides |

---

## Page 1: Customer Journey — 5 Score Cards

| Position | Measure Name | Display Units | Format | Conditional Color |
|----------|-------------|---------------|--------|-------------------|
| Card 1 | `Total Customers` | None | `#,##0` | Default (`#ECF0F1`) |
| Card 2 | `Active Customers` | None | `#,##0` | Default (`#ECF0F1`) |
| Card 3 | `Avg LTV VND` | Millions | `#,##0 "₫"` | Default (`#ECF0F1`) |
| Card 4 | `Avg Orders Per Customer` | None | `0.0` | Default (`#ECF0F1`) |
| Card 5 | `New Customers` | None | `#,##0` | `#2ECC71` (Green) |

### Step-by-step:
1. Drag **Card (new)** visual → resize to 230 × 110 → position at (20, 20)
2. Drag `Total Customers` measure into the **Fields** well
3. Format → Callout value → Display units: None → Format: `#,##0`
4. Category label: `"Total Customers"`
5. Duplicate the card 4 times (Ctrl+C → Ctrl+V), reposition per table above
6. Replace the measure in each duplicate with the correct one

---

## Page 2: Cashflow — 5 Score Cards

| Position | Measure Name | Display Units | Format | Conditional Color |
|----------|-------------|---------------|--------|-------------------|
| Card 1 | `Total Sales Revenue` | Millions | `#,##0 "₫"` | Default (`#ECF0F1`) |
| Card 2 | `Total Payments Received` | Millions | `#,##0 "₫"` | Default (`#ECF0F1`) |
| Card 3 | `Net Cashflow` | Millions | `#,##0 "₫"` | ✅ Conditional* |
| Card 4 | `Revenue MoM Growth %` | None | `0.0%` | ✅ Conditional* |
| Card 5 | `Payment Success Rate %` | None | `0.0%` | ✅ Conditional* |

### Conditional Formatting Rules:

**Card 3 — Net Cashflow:**
- Value ≥ 0 → `#2ECC71` (Green) 
- Value < 0 → `#E74C3C` (Red)
- *Setup:* Format → Callout value → Color → fx → Rules → Based on `Net Cashflow`

**Card 4 — Revenue MoM Growth %:**
- Value > 0 → `#2ECC71` (Green)
- Value = 0 → `#F1C40F` (Gold)
- Value < 0 → `#E74C3C` (Red)

**Card 5 — Payment Success Rate %:**
- Value > 90% → `#2ECC71` (Green)
- Value 70–90% → `#F39C12` (Amber)
- Value < 70% → `#E74C3C` (Red)

---

## Page 3: Payment Status — 5 Score Cards

| Position | Measure Name | Display Units | Format | Conditional Color |
|----------|-------------|---------------|--------|-------------------|
| Card 1 | `PS Total Orders` | None | `#,##0` | Default (`#ECF0F1`) |
| Card 2 | `Paid Orders` | None | `#,##0` | `#2ECC71` (Green) |
| Card 3 | `Payment Rate %` | None | `0.0%` | ✅ Conditional* |
| Card 4 | `Total Outstanding VND` | Millions | `#,##0 "₫"` | ✅ Conditional* |
| Card 5 | `Avg Payment Delay Hours` | None | `0.0` | ✅ Conditional* |

### Conditional Formatting Rules:

**Card 3 — Payment Rate %:**
- Value > 90% → `#2ECC71` (Green)
- Value 70–90% → `#F39C12` (Amber)
- Value < 70% → `#E74C3C` (Red)

**Card 4 — Total Outstanding VND:**
- Value ≤ 0 → `#2ECC71` (Green — all collected)
- Value > 0 → `#E74C3C` (Red — outstanding balance)

**Card 5 — Avg Payment Delay Hours:**
- Value ≤ 6 hrs → `#2ECC71` (Green)
- Value 6–24 hrs → `#F39C12` (Amber)
- Value > 24 hrs → `#E74C3C` (Red)

---

## Quick Setup Checklist

- [ ] Page 1: Create 5 Card (new) visuals with Customer Journey measures
- [ ] Page 2: Create 5 Card (new) visuals with Cashflow measures
- [ ] Page 3: Create 5 Card (new) visuals with Payment Status measures
- [ ] Apply `TechStore_theme.json` (View → Themes → Browse for themes)
- [ ] Set all card backgrounds to `#243447`
- [ ] Set border: `#3498DB`, radius 8px, width 1px
- [ ] Apply conditional formatting rules per page
- [ ] Verify display units (Millions for VND amounts, None for counts)
- [ ] Set category label font to 10pt, color `#95A5A6`
- [ ] Set callout value font to 28pt Semibold, color `#ECF0F1`

---

## Color Reference

| Color | Hex Code | Usage |
|-------|----------|-------|
| Dark Navy Background | `#1A2332` | Page background |
| Card Background | `#243447` | Card fill |
| Accent Blue | `#3498DB` | Card border |
| White Text | `#ECF0F1` | Default callout value |
| Subtitle Gray | `#95A5A6` | Category label |
| Positive Green | `#2ECC71` | Positive values |
| Warning Amber | `#F39C12` | Caution range |
| VIP Gold | `#F1C40F` | Neutral / zero growth |
| Danger Red | `#E74C3C` | Negative values |
