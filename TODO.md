# Turn Switch Assembly Symbol - Implementation Plan

**Created:** 2026-01-26  
**Status:** ✅ Completed

---

## 1. Overview

This document outlines the implementation plan for a new **Turn Switch Assembly Symbol**. 
Following the pattern established by the `emergency_stop_assembly_symbol`, we will create an assembly that combines:

- A **Turn Switch Actuator Symbol** (new graphic element)
- A **Normally Open (NO) Contact Symbol** (existing)

The result will be a visual representation of a turn switch that actuates a NO contact.

---

## 2. Symbol Design Reference

### 2.1 Existing Emergency Stop Assembly (Reference Pattern)

**Location:** `src/pyschemaelectrical/symbols/assemblies.py` → `emergency_stop_assembly_symbol()`

```
Assembly: NC Contact + Emergency Stop Button

       1 (Top Port)
       │
       ├───         ← NC Seat
      /
     /              ← Blade (closed)
    │
    2 (Bottom Port)
    
  ──●               ← Emergency Stop Mushroom Head (attached via linkage)
```

**Components:**
- `normally_closed_symbol()` - The contact
- `emergency_stop_button_symbol()` - The mushroom head actuator (semicircle polygon)
- Dashed linkage line connecting them

---

### 2.2 New Turn Switch Assembly

```
Assembly: NO Contact + Turn Switch Actuator

    1 (Top Port)
    │
     \             ← Blade (open, pointing left)
      \ 
       │
       2 (Bottom Port)

  ─┐
   │               ← Turn Switch Symbol (attached via dashed linkage)
   └─
```

**Components:**
- `normally_open_symbol()` - The contact (EXISTING)
- `turn_switch_symbol()` - The turn switch actuator (NEW)
- Dashed linkage line connecting them

---

## 3. Turn Switch Actuator Symbol Specification

### 3.1 Symbol Description

The turn switch actuator is an **"S-shaped" symbol made of 3 straight lines**:

```
Turn Switch Symbol (default orientation, 0° = horizontal attachment point on RIGHT):

    ─┐          ← TOP: horizontal line (half grid = 2.5mm), extends LEFT from top-right
     │          ← MID: vertical line (half grid = 2.5mm), connects top-left to bottom-right  
     └─         ← BOT: horizontal line (half grid = 2.5mm), extends RIGHT from bottom-left
```

### 3.2 Detailed Geometry

```
Coordinate System (Y↓ positive, X→ positive):

  Attachment point (linkage connects here) → (0, 0)
  
          (-2.5, -2.5) ─────── (0, -2.5)     ← TOP line
                       │
                       │                      ← MID line (vertical)
                       │
           (0, 2.5) ───────── (2.5, 2.5)     ← BOT line


Line Segments:
  TOP:  Point(-GRID_SIZE/2, -GRID_SIZE/2) → Point(0, -GRID_SIZE/2)
  MID:  Point(-GRID_SIZE/2, -GRID_SIZE/2) → Point(0, GRID_SIZE/2)  
  BOT:  Point(0, GRID_SIZE/2) → Point(GRID_SIZE/2, GRID_SIZE/2)

Where GRID_SIZE = 5.0mm, so GRID_SIZE/2 = 2.5mm
```

### 3.3 ASCII Diagram with Coordinates

```
              X-axis →
              -2.5    0    +2.5
               │      │      │
    Y  -2.5 ───●──────●      │     ← TOP horizontal line
    ↓          │      │      │
               │      │      │     ← MID vertical line (left side)
               │      │      │
       +2.5 ───│──────●──────●     ← BOT horizontal line
               │      │      │
               
    ● = vertex/corner point
    
    The RIGHT endpoints (at x=0 for top, x=+2.5 for bottom) 
    are where the linkage would connect.
```

### 3.4 Rotation Behavior

When `rotation=180` is applied (for left-side attachment like emergency stop):

```
Rotated 180° (attachment point now on LEFT):

     ─┘         ← Was BOT, now at top-right
    │           ← MID flipped
    ┌─          ← Was TOP, now at bottom-left
```

---

## 4. Complete Assembly Layout

### 4.1 Turn Switch Assembly (Assembled View)

```
            1 (Port)
            │
            │    ← Lead
           /     
          /      ← NO Blade (open)
         │
         │       ← Lead
         2 (Port)
         
    ╶╶╶─┐        ← Dashed linkage + Turn switch symbol
       │
       └─
```

### 4.2 Coordinate Layout

```
Y-Axis (↓ positive)

    -5.0 ─┬─ Port "1" position (0, -5)
          │
    -2.5 ─┤  Blade end zone
           \
     0.0 ─┼╶╶ Linkage starts here (0, 0), goes LEFT to (-2.5, 0)
           \
     2.5 ─┤  Blade start (0, 2.5)
          │
     5.0 ─┴─ Port "2" position (0, 5)

X-Axis:
    -5.0  -2.5   0    2.5
      │     │    │     │
      │  ─┐ │    │     │  ← Turn switch at (-2.5, 0) after translate
      │   │╶│    │     │  ← Dashed linkage
      │   └─│    │     │
```

---

## 5. Implementation Tasks

### WP-1: Create Turn Switch Actuator Symbol

**File:** `src/pyschemaelectrical/symbols/actuators.py`

**Task:** Add `turn_switch_symbol()` function

**Implementation:**
```python
def turn_switch_symbol(label: str = "", rotation: float = 0.0) -> Symbol:
    """
    Turn Switch Actuator (Manual Rotary).
    
    Geometry (0 deg = attachment point on RIGHT):
    - S-shaped symbol made of 3 straight lines.
    - Each line is GRID_SIZE/2 (2.5mm) long.
    - TOP: horizontal, from (-2.5, -2.5) to (0, -2.5)
    - MID: vertical, from (-2.5, -2.5) to (0, 2.5) - connects top-left to bottom-right
    - BOT: horizontal, from (0, 2.5) to (2.5, 2.5)
    
    Args:
        label: Component label (typically empty for actuator).
        rotation: Rotation in degrees (0 = right, 180 = left).
        
    Returns:
        Symbol: The turn switch actuator graphic.
    """
    style = standard_style()
    
    half_grid = GRID_SIZE / 2  # 2.5mm
    
    # TOP horizontal line: left half of top row
    top_line = Line(
        Point(-half_grid, -half_grid),  # (-2.5, -2.5)
        Point(0, -half_grid),           # (0, -2.5)
        style
    )
    
    # MID vertical line: connects top-left corner to bottom-right area
    mid_line = Line(
        Point(-half_grid, -half_grid),  # (-2.5, -2.5) - top left
        Point(0, half_grid),            # (0, 2.5) - bottom center
        style
    )
    
    # BOT horizontal line: right half of bottom row
    bot_line = Line(
        Point(0, half_grid),            # (0, 2.5)
        Point(half_grid, half_grid),    # (2.5, 2.5)
        style
    )
    
    elements = [top_line, mid_line, bot_line]
    
    sym = Symbol(elements, {}, label=label)
    
    if rotation != 0:
        sym = rotate(sym, rotation)
        
    return sym
```

**Subtasks:**
- [x] Add function to `actuators.py`
- [x] Add import to `symbols/__init__.py`
- [x] Add unit test in `tests/unit/test_symbols.py`

---

### WP-2: Create Turn Switch Assembly Symbol

**File:** `src/pyschemaelectrical/symbols/assemblies.py`

**Task:** Add `turn_switch_assembly_symbol()` function

**Implementation:**
```python
def turn_switch_assembly_symbol(label: str = "", pins: Tuple[str, str] = ("1", "2")) -> Symbol:
    """
    Turn Switch Assembly.
    
    Combines a Normally Open contact with a Turn Switch actuator.
    The Turn Switch is placed to the LEFT of the contact.
    
    Composition:
    - NO Contact (vertical, standard orientation)
    - Dashed mechanical linkage (GRID_SIZE/2 = 2.5mm to left)
    - Turn Switch S-shape at end of linkage
    
    Args:
        label: Component label (e.g. "-S1").
        pins: Tuple of 2 pin labels for the contact.
        
    Returns:
        Symbol: The composite turn switch assembly.
    """
    # 1. NO Contact (vertical)
    contact_sym = normally_open_symbol(label=label, pins=pins)
    
    # 2. Linkage (dashed line from contact center to left)
    linkage_len = GRID_SIZE / 2  # 2.5mm
    linkage_vector = Vector(-linkage_len, 0)  # Points left
    
    linkage = Line(
        Point(0, 0), 
        Point(linkage_vector.dx, linkage_vector.dy),
        Style(
            stroke=COLOR_BLACK, 
            stroke_width=LINE_WIDTH_THIN, 
            stroke_dasharray=LINKAGE_DASH_PATTERN
        )
    )
    
    # 3. Turn Switch actuator (rotated 180° so attachment is on right, facing the contact)
    actuator_sym = turn_switch_symbol(rotation=180)
    actuator_sym = translate(actuator_sym, linkage_vector.dx, linkage_vector.dy)
    
    # 4. Combine all elements
    all_elements = contact_sym.elements + [linkage] + actuator_sym.elements
    
    return Symbol(elements=all_elements, ports=contact_sym.ports, label=label)
```

**Required Imports (add to top of file):**
```python
from .actuators import emergency_stop_button_symbol, turn_switch_symbol
from .contacts import normally_closed_symbol, normally_open_symbol
```

**Subtasks:**
- [x] Add import: `turn_switch_symbol` from actuators
- [x] Add import: `normally_open_symbol` from contacts (if not already imported)
- [x] Add function to `assemblies.py`
- [x] Add export to `symbols/__init__.py`
- [x] Add unit test

---

### WP-3: Update Module Exports

**File:** `src/pyschemaelectrical/symbols/__init__.py`

**Changes Required:**
```python
# Update actuators import to include turn_switch_symbol
from .actuators import emergency_stop_button_symbol, turn_switch_symbol

# Update assemblies import to include turn_switch_assembly_symbol
from .assemblies import contactor_symbol, emergency_stop_assembly_symbol, turn_switch_assembly_symbol
```

---

### WP-4: Add Unit Tests

**File:** `tests/unit/test_symbols.py` (or create `tests/unit/test_actuators.py`)

**Tests to Add:**
```python
class TestTurnSwitchSymbol:
    """Tests for turn_switch_symbol."""
    
    def test_turn_switch_symbol_creation(self):
        """Test basic creation of turn switch symbol."""
        sym = turn_switch_symbol()
        assert sym is not None
        assert len(sym.elements) == 3  # TOP, MID, BOT lines
        
    def test_turn_switch_symbol_rotation(self):
        """Test rotation is applied."""
        sym = turn_switch_symbol(rotation=180)
        assert sym is not None
        # Elements should be transformed
        
    def test_turn_switch_symbol_has_no_ports(self):
        """Actuator symbols have no ports."""
        sym = turn_switch_symbol()
        assert len(sym.ports) == 0


class TestTurnSwitchAssemblySymbol:
    """Tests for turn_switch_assembly_symbol."""
    
    def test_turn_switch_assembly_creation(self):
        """Test basic creation of assembly."""
        sym = turn_switch_assembly_symbol()
        assert sym is not None
        
    def test_turn_switch_assembly_has_ports(self):
        """Assembly inherits ports from NO contact."""
        sym = turn_switch_assembly_symbol()
        assert "1" in sym.ports
        assert "2" in sym.ports
        
    def test_turn_switch_assembly_custom_pins(self):
        """Test custom pin labels."""
        sym = turn_switch_assembly_symbol(label="-S1", pins=("A", "B"))
        assert sym.label == "-S1"
```

---

### WP-5: Add Example Script (Optional)

**File:** `examples/example_turn_switch.py`

**Content:** Create a simple example demonstrating the turn switch assembly.

---

### WP-6: Documentation Updates

**Files to Update:**
- `README.md` - Add symbol to the symbols table
- `pyschemaelectrical_API_guide.md` - Add API documentation

---

## 6. Testing Checklist

- [x] All unit tests pass (`pytest tests/unit/`)
- [x] Integration tests pass (`pytest tests/integration/`)
- [x] Example script runs without error (if created)
- [x] SVG output renders correctly
- [x] Symbol dimensions are correct (half-grid = 2.5mm lines)

---

## 7. Dependencies

| Component | Status | Location |
|-----------|--------|----------|
| `normally_open_symbol` | ✅ Exists | `symbols/contacts.py` |
| `turn_switch_symbol` | ❌ **NEW** | `symbols/actuators.py` |
| `turn_switch_assembly_symbol` | ❌ **NEW** | `symbols/assemblies.py` |
| `translate()` | ✅ Exists | `utils/transform.py` |
| `rotate()` | ✅ Exists | `utils/transform.py` |
| `Line` | ✅ Exists | `model/primitives.py` |
| `standard_style()` | ✅ Exists | `model/parts.py` |
| `GRID_SIZE` | ✅ Exists | `model/constants.py` |

---

## 8. Notes & Considerations

1. **S-Shape Geometry**: The turn switch is 3 lines forming an S-shape. Each line is `GRID_SIZE/2` (2.5mm) long.

2. **Rotation Semantics**: Following `emergency_stop_button_symbol`, rotation is applied after symbol creation. Use `rotation=180` to have the attachment point on the left side.

3. **Port Inheritance**: The assembly inherits ports from the NO contact, not the actuator. This is consistent with the emergency stop assembly pattern.

4. **Linkage Length**: Using `GRID_SIZE / 2` (2.5mm) matches the emergency stop assembly for consistency.

---

## 9. Execution Order

1. **First:** Implement `turn_switch_symbol()` in `actuators.py` (WP-1)
2. **Second:** Implement `turn_switch_assembly_symbol()` in `assemblies.py` (WP-2)
3. **Third:** Update exports in `symbols/__init__.py` (WP-3)
4. **Fourth:** Add unit tests (WP-4)
5. **Fifth:** Run tests to verify (`pytest tests/`)
6. **Sixth:** Update documentation (WP-5, WP-6)
