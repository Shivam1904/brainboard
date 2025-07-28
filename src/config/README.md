# Grid Configuration

This directory contains configuration files for the Brainboard dashboard grid system.

## Grid Configuration (`grid.ts`)

The `grid.ts` file contains a centralized configuration for the grid layout that can be used by both TypeScript and CSS.

### Usage

```typescript
import { GRID_CONFIG, getGridCSSProperties, gridUtils } from './config/grid'

// Access grid settings
const columns = GRID_CONFIG.cols.lg // 32
const rowHeight = GRID_CONFIG.rowHeight // 20px
const margin = GRID_CONFIG.margin // [8, 8]

// Get CSS custom properties for styling
const cssProps = getGridCSSProperties()
// Returns: {
//   '--grid-cols': '32',
//   '--grid-row-height': '20px',
//   '--grid-margin-vertical': '8px',
//   '--grid-margin-horizontal': '8px',
//   '--grid-container-padding-vertical': '8px',
//   '--grid-container-padding-horizontal': '8px',
//   '--grid-lines-opacity': '0.4'
// }

// Use utility functions
const itemWidth = gridUtils.getItemWidth(3, 1200) // Calculate width for 3-column widget
const itemHeight = gridUtils.getItemHeight(4) // Calculate height for 4-row widget
const isValid = gridUtils.isValidPosition(0, 0, 3, 4) // Check if position is valid
const maxRows = gridUtils.getMaxRows(window.innerHeight) // Get max available rows
const constrainedLayout = gridUtils.constrainLayout(layout) // Constrain layout to boundaries
```

### Configuration Options

- **cols**: Number of columns in the grid (currently 32 for large screens)
- **rowHeight**: Height of each grid row in pixels (20px)
- **margin**: Margin between grid items [vertical, horizontal] (8px each)
- **containerPadding**: Padding around the grid container [vertical, horizontal] (8px each)
- **breakpoints**: Responsive breakpoints for different screen sizes
- **gridLines**: Configuration for grid line display (opacity, color)
- **maxSearchDepth**: Maximum rows to search when finding empty space for new widgets

### CSS Integration

The grid configuration automatically sets CSS custom properties that are used in `src/index.css`:

```css
/* Grid lines use the config values */
.react-grid-layout.show-grid-lines {
  background-size: calc(100% / var(--grid-cols)) var(--grid-row-height);
}
```

### Benefits

1. **Single Source of Truth**: All grid settings are defined in one place
2. **Type Safety**: TypeScript ensures correct usage of grid values
3. **CSS Integration**: CSS automatically uses the same values via custom properties
4. **Easy Maintenance**: Change grid settings in one place, affects both TS and CSS
5. **Extensible**: Easy to add new grid-related configurations
6. **Boundary Constraints**: Widgets are constrained to stay within viewport (applied on drag/resize stop)
7. **Visual Feedback**: Users get visual feedback when widgets are constrained
8. **Performance Optimized**: Constraints applied only when needed, not during every drag/resize event

### Modifying Grid Settings

To change grid settings, simply update the `GRID_CONFIG` object in `grid.ts`. The changes will automatically apply to:

- React Grid Layout component
- CSS grid lines
- Widget positioning logic
- All utility functions

Example:
```typescript
// Change to 24 columns instead of 32
export const GRID_CONFIG = {
  cols: {
    lg: 24, // Changed from 32
  },
  // ... rest of config
}
``` 