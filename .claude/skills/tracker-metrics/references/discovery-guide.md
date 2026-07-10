# Discovery Guide

How to scan the tracker and build the knowledge base from scratch.

## Prerequisites

- Chrome DevTools MCP connected to a browser session
- User authenticated on `tracker.zingplay.com` (Azure AD login)

## Step 1: Extract menu structure

Navigate to any tracker page, then extract the full menu tree via JS:

```javascript
() => {
  const nav = document.querySelector('nav, .navbar, [role="navigation"]');
  if (!nav) return { error: 'No navigation found' };

  const menuItems = [];
  const topItems = nav.querySelectorAll(':scope > ul > li, :scope > .navbar-nav > li');

  topItems.forEach(li => {
    const topLink = li.querySelector(':scope > a');
    if (!topLink) return;

    const item = {
      label: topLink.textContent.trim(),
      href: topLink.getAttribute('href'),
      children: []
    };

    const subLinks = li.querySelectorAll('ul a, .dropdown-menu a');
    subLinks.forEach(a => {
      const href = a.getAttribute('href');
      // Skip empty links (headers/dividers) and anchors
      if (href && href !== '#' && href !== '' && !href.startsWith('#')) {
        item.children.push({
          label: a.textContent.trim(),
          href: href
        });
      }
    });

    if (item.children.length > 0) {
      menuItems.push(item);
    }
  });

  return menuItems;
}
```

Save the result to `.tracker/site-map.json` with a timestamp:

```json
{
  "scanned_at": "2026-02-27",
  "base_url": "https://tracker.zingplay.com",
  "menus": [ ... ]
}
```

## Step 2: Scan each page

For each page URL found in the site-map:

### 2a. Navigate and wait for load

```
navigate_page(url) → wait_for(["Search"]) or wait_for(["Highcharts"])
```

Some pages may not have a Search button or charts — handle gracefully. Set a timeout of 10 seconds.

### 2b. Detect form fields

Take a snapshot and extract form-related elements:

```javascript
() => {
  const fields = [];

  // Look for labeled inputs, selects, and custom dropdowns
  const labels = document.querySelectorAll('label, .control-label');
  labels.forEach(label => {
    const text = label.textContent.trim();
    const input = label.querySelector('input, select') ||
                  label.nextElementSibling?.querySelector('input, select');
    fields.push({
      label: text,
      type: input?.tagName?.toLowerCase() || 'custom-dropdown',
      currentValue: input?.value || null
    });
  });

  // Also check for date inputs specifically
  document.querySelectorAll('input[type="date"], input[type="text"]').forEach(el => {
    const label = el.closest('.form-group')?.querySelector('label')?.textContent?.trim();
    if (label && !fields.find(f => f.label === label)) {
      fields.push({ label, type: 'input', currentValue: el.value });
    }
  });

  return fields;
}
```

### 2c. Extract chart metadata

Run the bundled `highcharts-utils.js` to get chart titles and series names. For the page profile, only store metadata — not full data:

```javascript
// After running highcharts-utils.js, extract just the structure
() => {
  if (!window.Highcharts?.charts) return [];
  return window.Highcharts.charts.filter(c => c).map(chart => ({
    title: chart.title?.textStr || '',
    subtitle: chart.subtitle?.textStr || '',
    seriesNames: chart.series.map(s => s.name),
    seriesTypes: [...new Set(chart.series.map(s => s.type))],
    yAxes: [...new Set(chart.series.map(s =>
      s.yAxis?.options?.title?.text).filter(Boolean))],
    hasData: chart.series.some(s => s.data.length > 0)
  }));
}
```

### 2d. Save page profile

Save to `.tracker/page-profiles/<slug>.json`:

```json
{
  "url": "/gsnreport/accactive",
  "title": "Account New & Active",
  "scanned_at": "2026-02-27",
  "form_fields": [
    { "label": "Country", "type": "custom-dropdown", "currentValue": "--All--" },
    { "label": "AppName", "type": "custom-dropdown", "currentValue": "buraco_it" },
    { "label": "From", "type": "input", "currentValue": "2026-01-26" },
    { "label": "To", "type": "input", "currentValue": "2026-02-27" }
  ],
  "charts": [
    {
      "title": "A1",
      "seriesNames": ["A1_Android", "A1", "ActiveDevice_Android", "A1_iOS", "ActiveDevice_iOS"],
      "seriesTypes": ["column", "line"],
      "yAxes": ["#"],
      "hasData": true
    }
  ]
}
```

Use the URL path slug as filename: `/gsnreport/accactive` → `accactive.json`

## Step 3: Build initial catalog

After scanning pages, generate `.tracker/metrics-catalog.md` by:

1. Grouping metrics by page
2. Drafting descriptions based on metric names, series names, and page title context
3. Inferring basic relationships (metrics on the same page are likely related)
4. Marking the catalog as `status: draft` — it will be enriched through usage

See `catalog-schema.md` for the exact format.

## Incremental re-scan

When re-scanning, compare with existing site-map:
- **New pages**: scan and add profiles
- **Removed pages**: mark as inaccessible (user permissions may have changed)
- **Existing pages**: re-scan only if user requests or profile is older than 30 days
