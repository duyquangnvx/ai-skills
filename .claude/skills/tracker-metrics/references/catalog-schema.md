# Catalog Schema

Defines the format for all state files stored in `.tracker/`.

## Directory structure

```
.tracker/
├── site-map.json              # Menu structure (what pages user can access)
├── metrics-catalog.md         # Knowledge base: metrics, descriptions, relationships
└── page-profiles/             # Per-page metadata (form fields, chart configs)
    ├── accactive.json
    ├── qualityjserror.json
    ├── cashdaily18.json
    └── ...
```

## site-map.json

```json
{
  "scanned_at": "2026-02-27",
  "base_url": "https://tracker.zingplay.com",
  "menus": [
    {
      "label": "Account",
      "children": [
        { "label": "New & Active", "href": "https://tracker.zingplay.com/gsnreport/accactive" },
        { "label": "Platform", "href": "https://tracker.zingplay.com/gsnreport/accplatform" }
      ]
    },
    {
      "label": "Quality",
      "children": [
        { "label": "JS Error", "href": "https://tracker.zingplay.com/gsnreport/qualityjserror" },
        { "label": "CCU", "href": "https://tracker.zingplay.com/gsnreport/qualityccu" }
      ]
    }
  ]
}
```

**Update rules:**
- Overwrite entirely on each discovery scan
- Timestamp tracks freshness

## page-profiles/{slug}.json

```json
{
  "url": "/gsnreport/accactive",
  "title": "Account New & Active",
  "menu_path": "Account > New & Active",
  "scanned_at": "2026-02-27",
  "form_fields": [
    { "label": "Country", "type": "custom-dropdown" },
    { "label": "AppName", "type": "custom-dropdown" },
    { "label": "From", "type": "date-input" },
    { "label": "To", "type": "date-input" },
    { "label": "Platform", "type": "custom-dropdown", "location": "advanced" }
  ],
  "charts": [
    {
      "title": "A1",
      "seriesNames": ["A1_Android", "A1", "A1_iOS"],
      "seriesTypes": ["column", "line"],
      "yAxes": ["#"],
      "hasData": true
    },
    {
      "title": "Retention Rate",
      "seriesNames": ["RR1", "RR3", "RR7", "RR15", "RR30"],
      "seriesTypes": ["line"],
      "yAxes": ["%"],
      "hasData": true
    }
  ],
  "notes": "Page footer explains: RRx = % of N1 active on day N+x. Churn = % A1 not active after X days."
}
```

**Slug naming:** extract from URL path — `/gsnreport/accactive` → `accactive.json`, `/gsnreport/quality/stepflow` → `quality-stepflow.json` (replace `/` with `-`).

**Update rules:**
- Overwrite on rescan of that specific page
- `notes` field: append-only, captures useful context from page footers or user corrections

## metrics-catalog.md

This is the most important file — the agent's domain knowledge base.

### Format

```markdown
# Metrics Catalog
Status: active
Last updated: 2026-02-27
Apps scanned: buraco_it

---

## A1 (Daily Active Accounts)
- **Page**: Account > New & Active (`/gsnreport/accactive`)
- **Description**: Number of unique accounts that logged in on a given day
- **Series**: A1 (total), A1_Android, A1_iOS
- **Chart type**: column (per-platform) + line (total)
- **Unit**: # (count)
- **Related metrics**: N1, Retention Rate, Churn Rate, A3/A7/A15/A30, CCU
- **When drops**: Check N1 (acquisition), Churn (attrition), Quality Errors (technical), GameChange (updates)
- **When spikes**: Check marketing campaigns, game events, featuring on store
- **Tags**: health-core, user

### Observations
- [2026-02-27] buraco_it typical range: 45-65 daily
- [2026-02-27] Weekend values slightly lower than weekdays

---

## N1 (Daily New Accounts)
- **Page**: Account > New & Active (`/gsnreport/accactive`)
- **Description**: Number of new accounts created on a given day
- **Series**: N1 (total), N1_Android, N1_iOS, Install_Android, Install_iOS
- **Chart type**: column (per-platform) + line (total)
- **Unit**: # (count)
- **Related metrics**: A1, Install Quality, Conversion Rate
- **When drops**: Check Install Quality, store ranking, marketing spend
- **When spikes**: Check campaign launches, store featuring
- **Tags**: health-core, acquisition

---

## JS Error
- **Page**: Quality > JS Error (`/gsnreport/qualityjserror`)
- **Description**: JavaScript errors logged from game clients
- **Series**: ErrorQty (error count), DeviceQty (unique devices with errors)
- **Chart type**: line
- **Unit**: # (count)
- **Related metrics**: A1, Churn Rate, Loading Fail, Error Overview
- **When spikes**: Check GameChange (recent updates), OS Version distribution
- **Diagnostic tip**: ErrorQty >> DeviceQty means one device repeating errors; ErrorQty ~ DeviceQty means widespread issue
- **Tags**: health-core, quality
```

### Tag system

Tags enable the agent to quickly find metrics for specific tasks:

| Tag | Used for | Example metrics |
|---|---|---|
| `health-core` | Health report — always included | A1, N1, Revenue, Error, Churn, CCU |
| `user` | User-related investigations | A1, N1, Retention, Churn, A3/A7/A15/A30 |
| `revenue` | Revenue investigations | Revenue Gross/Net, ARPU, ARPPU, Paying Rate, Cash |
| `quality` | Quality investigations | JS Error, Loading Fail, Error Overview, CCU |
| `acquisition` | User acquisition investigations | N1, Install Quality, Conversion Rate |

### Update rules

| Trigger | What to update | How |
|---|---|---|
| Discovery scan | Metric entries (page, series, chart type) | Overwrite structure, preserve observations |
| After serving a request | Observations section | Append new dated observation |
| User correction | Description, relationships, tags | Edit in place |
| New metric discovered | New entry | Append to catalog |

### Guidelines for observations

Good observations are **specific and reusable**:
- "buraco_it A1 normal range: 45-65 weekdays" (useful for future anomaly detection)
- "JS Error spike 02-16 correlated with game update 02-15" (useful for future diagnostics)

Bad observations are **one-time facts with no future value**:
- "User asked about A1 on 02-27" (session-specific, not useful)
- "Extracted 3 charts from accactive page" (operational detail, not insight)
