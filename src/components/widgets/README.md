# Widget Components

This directory contains all the widget components for the Brainboard system.

## Implemented Widgets

### Everyday Web Search Widget (`EverydayWebSearchWidget.tsx`)

**Status**: ✅ Implemented with dummy data

**Features**:
- Displays scheduled web searches for the current day
- Shows search results with headings, subheadings, text content, and images
- Loading states and error handling
- Responsive design with scrollable content
- Placeholder for chart data visualization

**API Integration**:
- Ready for backend integration with API endpoints defined in `src/config/api.ts`
- Currently uses dummy data for development
- Easy to switch to real API calls by uncommenting the import and API calls

**Dummy Data**:
- 3 sample web searches: AI developments, Stock market trends, Weather forecast
- Each search result includes formatted content with images
- Timestamps and search terms are displayed

**Usage**:
The widget is automatically included in the dashboard and can be added via the "Add Widget" button. It's configured as a medium-sized widget (10x8) and supports resizing and dragging.

**Next Steps**:
1. Uncomment API imports when backend is ready
2. Replace dummy data with real API calls
3. Add chart visualization for search result data
4. Implement real-time updates for new search results

## Planned Widgets

All other widgets are planned for implementation. See `src/config/widget-functionality.md` for detailed specifications. 