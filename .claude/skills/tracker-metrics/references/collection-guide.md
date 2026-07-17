# Collection Guide

How to navigate tracker pages, fill query forms, and extract Highcharts data.

## Prerequisites

- Chrome DevTools MCP connected
- Page profile available in `.tracker/page-profiles/` (or discover dynamically)
- Target page URL known (from site-map or metrics-catalog)

## Navigation flow

### 1. Navigate to page

```
navigate_page(url, type="url") → wait for page load
```

Wait for either the Search button or chart content to appear:
```
wait_for(["Search", "Highcharts"], timeout=10000)
```

### 2. Detect form fields

If a page profile exists, use the cached field list. Otherwise, take a snapshot to discover fields:

```
take_snapshot() → identify form elements by their labels
```

Common field types across tracker pages:

| Field | How to detect | How to fill |
|---|---|---|
| AppName | Custom dropdown with search | Click to open → type in search box → click option |
| Platform | Custom dropdown | Click to open → click option text |
| Country | Custom dropdown with search | Click to open → type in search box → click option |
| From / To | Text input (date) | fill(uid, "YYYY-MM-DD") |
| Search button | Button labeled "Search" | click(uid) |

### 3. Fill form fields

#### Date fields (From / To)

Straightforward — use `fill` with ISO date format:
```
fill(from_uid, "2025-12-01")
fill(to_uid, "2025-12-31")
```

#### Custom dropdowns (AppName, Platform, Country)

These are not native `<select>` elements. They are custom components with a hidden textbox:

1. Click the current value text to open the dropdown
2. A list of options appears as StaticText elements
3. Click the desired option

```
take_snapshot() → find the dropdown display text (e.g., "AllPlatform")
click(display_text_uid) → dropdown opens
take_snapshot() → find the option (e.g., "Android")
click(option_uid)
```

If the dropdown has a search box (AppName, Country), type into it to filter:
```
click(display_text_uid) → opens dropdown
take_snapshot() → find the search textbox inside dropdown
fill(search_textbox_uid, "buraco") → filters options
take_snapshot() → find filtered option
click(option_uid)
```

#### Advanced filters

Some pages have an "Advanced Filter" toggle that reveals additional fields. If needed:
```
click("Advanced Filter" link/button) → take_snapshot() → fill revealed fields
```

### 4. Submit query

```
click(search_button_uid)
wait_for(["Highcharts"], timeout=15000)
```

Allow extra time for pages with many charts (Account New & Active has 12 charts).

## Data extraction

### Using the bundled script

Read `scripts/highcharts-utils.js` and run it via `evaluate_script`:

```
evaluate_script({ function: <contents of highcharts-utils.js> })
```

The script returns:
```json
{
  "summary": {
    "totalCharts": 3,
    "chartTitles": ["A1", "N1", "Revenue Gross"],
    "seriesCount": 10,
    "totalDataPoints": 330
  },
  "charts": [
    {
      "title": "A1",
      "subtitle": "buraco_it - AllPlatform",
      "categories": ["01-26", "01-27", ...],
      "series": [
        {
          "name": "A1_Android",
          "data": [49, 38, 43, ...],
          "type": "column",
          "stack": "A1",
          "yAxis": "#",
          "visible": true
        }
      ]
    }
  ]
}
```

### Handling large responses

Some pages return 1000+ data points. If the response is too large:

1. First get just the summary to understand scope
2. Then extract specific charts by index if needed:

```javascript
() => {
  const chart = window.Highcharts.charts.filter(c => c)[0]; // specific chart
  return {
    title: chart.title?.textStr,
    categories: chart.xAxis?.[0]?.categories || [],
    series: chart.series.map(s => ({
      name: s.name,
      data: s.options.data || [],
      type: s.type,
      visible: s.visible,
    }))
  };
}
```

### Data with null values

Tracker data frequently contains `null` values for days with no activity. When presenting data:
- Note which dates have null vs zero (they mean different things)
- `null` = no data recorded for that day
- `0` = data was recorded, value is zero

## Edge cases

### Page with no charts
Some pages may be config/admin pages without Highcharts. The utils script returns `{ error: 'Highcharts not available' }`. Skip these during data collection.

### Charts with no data
A chart may exist but have empty series (e.g., "OSVersion" chart on JS Error page). The `hasData` field in the summary helps identify these — skip empty charts in analysis.

### Loading timeouts
If `wait_for` times out, the page might be slow or the query returned no results. Take a screenshot to diagnose before retrying.

### Session expiry
If navigating returns a Microsoft login page (redirect to `login.microsoftonline.com`), the session has expired. Inform the user they need to re-authenticate.
