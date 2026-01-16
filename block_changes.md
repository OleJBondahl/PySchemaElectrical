# Dynamic Block Symbol - Needed Changes

## Current Limitation

The `dynamic_block_symbol` function only supports **uniform pin spacing**:

```python
def dynamic_block_symbol(
    label: str = '',
    top_pins: Optional[Tuple[str, ...]] = None,
    bottom_pins: Optional[Tuple[str, ...]] = None,
    pin_spacing: float = 10.0  # <-- uniform spacing only
) -> Symbol
```

## Use Case: PSU Shared Output Block

When placing multiple PSU circuits side by side with a shared dynamic block underneath, the PSU output pins don't align with uniform spacing.

**Example with 2 PSUs at 40mm spacing:**

```
PSU1 (x=0)          PSU2 (x=40)
  24V  GND            24V  GND
   |    |              |    |
   x=0  x=10          x=40  x=50
```

Required pin positions: `[0, 10, 40, 50]`
Required spacing pattern: `[10, 30, 10]` (non-uniform)

## Proposed Solution

Add support for explicit pin positions in `dynamic_block_symbol`:

### Option A: Pin positions tuple

```python
def dynamic_block_symbol(
    label: str = '',
    top_pins: Optional[Tuple[str, ...]] = None,
    bottom_pins: Optional[Tuple[str, ...]] = None,
    pin_spacing: float = 10.0,
    # NEW: explicit positions override uniform spacing
    top_pin_positions: Optional[Tuple[float, ...]] = None,
    bottom_pin_positions: Optional[Tuple[float, ...]] = None,
) -> Symbol
```

Usage:
```python
dynamic_block_symbol(
    label="U1",
    top_pins=("+1", "-1", "+2", "-2"),
    top_pin_positions=(0.0, 10.0, 40.0, 50.0),  # explicit x-offsets
)
```

### Option B: Pin definitions with position

```python
from typing import NamedTuple

class PinDef(NamedTuple):
    label: str
    x_offset: float

def dynamic_block_symbol(
    label: str = '',
    top_pins: Optional[Tuple[Union[str, PinDef], ...]] = None,
    bottom_pins: Optional[Tuple[Union[str, PinDef], ...]] = None,
    pin_spacing: float = 10.0,  # used when pin is just a string
) -> Symbol
```

Usage:
```python
dynamic_block_symbol(
    label="U1",
    top_pins=(
        PinDef("+1", 0.0),
        PinDef("-1", 10.0),
        PinDef("+2", 40.0),
        PinDef("-2", 50.0),
    ),
)
```

## Block Width Calculation

With explicit positions, the block width should be calculated as:
```python
max_x = max(top_pin_positions or [0])
min_x = min(top_pin_positions or [0])
# Same for bottom pins
width = max(all_max_x) - min(all_min_x) + GRID_SIZE  # padding
```

## Backward Compatibility

Both options maintain backward compatibility:
- If `top_pin_positions` is `None`, use uniform `pin_spacing` (current behavior)
- If `top_pin_positions` is provided, use explicit positions

## Recommendation

**Option A** is simpler and more explicit. The positions tuple maps 1:1 with the pin labels tuple, making it clear which pin goes where.
