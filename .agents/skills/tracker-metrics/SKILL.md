---
name: tracker-metrics
description: >
  ALWAYS invoke this skill when the user asks about game metrics, KPIs, error rates, revenue,
  user counts, retention, churn, CCU, A1, N1, or any data from tracker.zingplay.com.
  Do NOT fetch game metrics, navigate the tracker dashboard, or analyze game performance data
  without consulting this skill first — it contains extraction scripts, a self-improving knowledge
  base, and analysis patterns that produce significantly better results than ad-hoc browser
  interaction. Do NOT attempt to extract Highcharts data manually or write custom chart-scraping
  code — this skill bundles tested extraction utilities. Also invoke when user asks diagnostic
  questions like "why did A1 drop", "game health report", "JS errors this week",
  "compare revenue this month vs last month", or any request involving game performance analysis,
  even if "tracker" is not mentioned explicitly.
---

# Tracker Metrics

Collect and analyze game metrics from tracker.zingplay.com. This skill enables three modes: fetching specific metrics, generating health reports, and diagnosing anomalies. It maintains a self-improving knowledge base that gets smarter with each use.

## Required tools

- **Chrome DevTools MCP** — for browser navigation and interaction
- User must be authenticated on `tracker.zingplay.com` (Azure AD)

## Knowledge base

The skill maintains state in `.tracker/` that persists across sessions:

- `site-map.json` — accessible menu pages (role-dependent per user)
- `metrics-catalog.md` — metric descriptions, relationships, accumulated observations
- `page-profiles/` — per-page form fields and chart configurations

If `.tracker/` does not exist, run the Discovery flow first.

---

## PRE-FLIGHT CHECKLIST

Complete this checklist before ANY data work. Do NOT skip steps or proceed without verification.

- [ ] **Chrome DevTools available?** Verify the Chrome DevTools MCP tool is accessible. If unavailable, inform the user: "I need Chrome DevTools MCP to interact with the tracker. Please ensure it's connected." and stop.
- [ ] **Read the metrics catalog.** If `.tracker/metrics-catalog.md` exists, read it NOW — it contains accumulated domain knowledge (typical ranges, correlations, seasonal patterns) that makes analysis faster and more accurate. If it does not exist, proceed to DISCOVERY flow.
- [ ] **Read `scripts/highcharts-utils.js`.** This file contains tested extraction logic. You will need its contents for any chart data extraction. Do NOT write custom Highcharts extraction code — the utility handles edge cases (multiple axes, mixed chart types, empty series) that ad-hoc code will miss.

Only after completing all checkpoints, proceed to HANDLE_REQUEST.

---

## MAIN FLOW: HANDLE_REQUEST

1. Parse user intent
   - If user asks for specific metric data (e.g., "get JS errors for buraco_it in December") → **DIRECT_FETCH**
   - If user asks for an overview or health report (e.g., "game health report this week") → **HEALTH_REPORT**
   - If user asks a diagnostic question (e.g., "why did A1 drop yesterday?") → **DIAGNOSTIC**
   - If user asks to rescan or refresh the tracker map → **DISCOVERY**
   - Otherwise, use the catalog to determine which metrics are relevant → **DIRECT_FETCH**

---

### SUB_FLOW: DIRECT_FETCH

1. **Find the metric**
   - Search catalog for the requested metric by name, tag, or description
   - If NOT found → reply with available metrics from catalog, ask user to clarify, **End**

2. **Collect data**
   - Call **NAVIGATE_AND_EXTRACT** with: page URL, AppName, Platform, date range from user request
   - If extraction fails → reply with error, suggest checking authentication, **End**

3. **Present results**
   - Format chart data as markdown tables
   - Highlight anomalies (spikes/drops) in bold — use patterns from `references/analysis-patterns.md` if dealing with complex or multi-metric data (for simple single-metric fetches, standard table formatting is sufficient)
   - Call **UPDATE_CATALOG** with any new observations
   - **End**

---

### SUB_FLOW: HEALTH_REPORT

Health reports aggregate multiple metrics into a single assessment. The value comes from cross-referencing metrics against each other — a revenue drop alone is ambiguous, but a revenue drop + A1 drop + error spike tells a clear story.

1. **Determine scope**
   - Read catalog → collect all metrics tagged `health-core`
   - Default set: A1, N1, Revenue, JS Error/Quality Error, Churn, CCU
   - Determine date range from user request (default: last 7 days)
   - Determine AppName and Platform from user request

2. **Collect metrics from multiple pages**
   - Group metrics by page (metrics on the same page are collected in one visit to save time)
   - **DO:**
     - Navigate to next page
     - Call **NAVIGATE_AND_EXTRACT**
     - Store extracted data
   - **LOOP UNTIL:**
     - All pages visited
     - OR extraction fails **3 consecutive times** → proceed with partial data and note which metrics are missing

3. **Analyze**
   - For each metric: calculate trend (stable/growing/declining), identify anomalies
   - Cross-reference relationships from catalog — this is where the catalog's accumulated observations pay off. For example, if A1 dropped and the catalog notes "JS error spike on date X caused A1 drop previously", check JS errors for the same period.
   - BEFORE writing the report, read `references/analysis-patterns.md` for the health report template and analysis techniques. The template ensures consistent, actionable reports. Do NOT write the report without consulting the template.

4. **Present report**
   - Executive summary first (1-3 sentences: overall health + most important finding)
   - Then per-metric details with trend indicators
   - Call **UPDATE_CATALOG** with new observations
   - **End**

---

### SUB_FLOW: DIAGNOSTIC

Diagnostics are the most valuable mode because they answer "why", not just "what". The approach: confirm the anomaly, then systematically check related metrics using the catalog's relationship graph.

1. **Fetch the questioned metric**
   - Identify which metric the user is asking about
   - Call **NAVIGATE_AND_EXTRACT** for that metric's page

2. **Confirm the anomaly**
   - Analyze the data: is there actually a drop/spike on the date in question?
   - If data looks normal → reply "The data appears normal for {date}" with evidence (show the numbers), **End**
   - Otherwise, quantify the anomaly: % deviation from typical range, comparison to catalog observations if available

3. **Investigate related metrics**
   - Read catalog → get the "When drops/spikes" relationships for this metric
   - If the catalog has no relationships yet (early stage), use these defaults: for user metrics (A1/N1) check error metrics and revenue; for error metrics check deployment dates; for revenue check user metrics and payment errors
   - **DO:**
     - Pick next related metric from relationship list
     - Call **NAVIGATE_AND_EXTRACT**
     - Analyze: does this related metric show a correlated change in the same timeframe?
   - **LOOP UNTIL:**
     - A likely cause is identified (correlated change found)
     - OR all related metrics checked
     - OR **5 pages** visited (prevent runaway investigation)

4. **Build diagnosis**
   - If a root cause is identified: explain with evidence, show the correlation (metric A dropped X% on date Y, metric B spiked Z% on the same date, which is consistent with pattern P from catalog)
   - If inconclusive: list what was checked, what was ruled out, and suggest next steps the user could investigate
   - Call **UPDATE_CATALOG** with new observations and any newly discovered relationships
   - **End**

---

## TRIGGER FLOW: DISCOVERY

*Trigger*: Knowledge base does not exist OR user asks to scan/refresh/rescan

Discovery builds the knowledge base from scratch by crawling the tracker's menu and pages. This is a one-time setup that dramatically speeds up all future interactions.

BEFORE starting discovery, read `references/discovery-guide.md` — it contains the JS snippets for menu extraction, form field detection, and chart metadata extraction. Do NOT write custom discovery scripts; the reference file has tested code that handles the tracker's specific UI patterns (custom dropdowns, dynamic loading, role-based menus).

1. **Extract menu structure**
   - Navigate to any tracker page
   - Run the menu extraction script from `references/discovery-guide.md`
   - Save result to `.tracker/site-map.json`

2. **Scan accessible pages**
   - **DO:**
     - Navigate to next page from site-map
     - Detect form fields (snapshot + JS extraction per `references/discovery-guide.md`)
     - Run chart metadata extraction (titles, series names, types — not full data)
     - Save page profile to `.tracker/page-profiles/{slug}.json`
   - **LOOP UNTIL:**
     - All pages scanned
     - OR **20 pages** scanned → checkpoint: inform user of progress, continue if they want

3. **Build metrics catalog**
   - Read all page profiles
   - Generate `.tracker/metrics-catalog.md` following the schema in `references/catalog-schema.md`
   - Contents: metric names, pages, series, chart types
   - Draft descriptions based on metric names and page context
   - Infer basic relationships (metrics on same page are likely related)
   - Tag core metrics as `health-core`: A1, N1, Revenue, JS Error, Quality Error, Churn, CCU
   - Mark catalog `status: draft` — it will improve automatically through the UPDATE_CATALOG routine as the user runs analyses

4. **Report to user**
   - "Scanned {N} pages, found {M} metrics across {K} charts. The catalog is ready."
   - List the top-level categories discovered
   - **End**

---

## NAVIGATE_AND_EXTRACT ROUTINE

This is the core browser interaction routine. The tracker uses custom UI components (not standard HTML selects) that require specific interaction patterns.

BEFORE first use in a session, read `references/collection-guide.md` for the dropdown interaction pattern and form-filling techniques. The tracker's dropdowns are custom components that don't respond to standard fill() — the collection guide has the tested interaction sequence. Do NOT attempt to fill dropdowns without reading this guide; it will fail silently and return data for the wrong app/platform.

1. **Navigate to page**
   - `navigate_page(url)`
   - `wait_for(["Search"], timeout=10000)`
   - If timeout → take screenshot to diagnose
   - If redirect to `login.microsoftonline.com` → inform user: "Your tracker session has expired. Please log in again at tracker.zingplay.com, then let me know when you're ready." and **return error**

2. **Fill query form**
   - `take_snapshot()` to identify form elements
   - Fill date fields: `fill(from_uid, date)`, `fill(to_uid, date)`
   - Fill dropdowns (AppName, Platform, Country): use the custom dropdown interaction pattern from `references/collection-guide.md`
   - If a required field cannot be filled (dropdown option not found) → **return error** with field name and available options
   - Click Search button
   - `wait_for(["Highcharts"], timeout=15000)`
   - If timeout → take screenshot, **return error** with screenshot context

3. **Extract chart data**
   - Use the contents of `scripts/highcharts-utils.js` already loaded during pre-flight
   - `evaluate_script(highcharts_utils_code)` — returns `{ summary, charts }`
   - Validate: if `charts` array is empty but page appeared to have charts, take screenshot and retry once
   - **Return** the structured data

---

## UPDATE_CATALOG ROUTINE

Run after every data collection and analysis. This routine is what makes the skill compound in value over time — each use enriches the catalog with observations that help future analyses.

1. Read current `.tracker/metrics-catalog.md`

2. Determine what's new:
   - New metric not in catalog → add entry with page, series, chart type
   - New observation (typical range, anomaly pattern, correlation) → append to Observations section with date
   - New relationship discovered → update Related metrics and When drops/spikes sections

3. Write updated catalog
   - Preserve all existing content — never overwrite existing observations
   - Append new observations with ISO date prefix
   - Update structural fields only if page profile changed

**What makes a good observation** — record information that helps future analysis:
- Typical value ranges: "A1 for buraco_it: 45-65 weekday, 35-50 weekend"
- Confirmed correlations: "JS error spike 02-16 caused A1 drop, triggered by game update 02-15"
- Seasonal patterns: "Revenue peaks on Sundays for this app"
- Data quirks: "Loading Fail page has no Hourly chart, only Daily"

Do NOT record session logistics ("user asked about X") or operational noise ("extracted 3 charts successfully").

---

## Reference files

These files contain critical knowledge for specific operations. Read them at the points specified in the flows above — each pointer tells you exactly when to read.

- `references/catalog-schema.md` — Schema specification for `.tracker/metrics-catalog.md`. Read when building or restructuring the catalog during DISCOVERY.
- `references/analysis-patterns.md` — Report templates and analysis techniques for health reports and diagnostics. Read BEFORE writing any health report or diagnostic analysis.
- `references/discovery-guide.md` — JS snippets and procedures for menu extraction, form detection, and chart metadata scanning. Read BEFORE starting DISCOVERY flow.
- `references/collection-guide.md` — Form-filling techniques and the custom dropdown interaction pattern specific to the tracker's UI. Read BEFORE first NAVIGATE_AND_EXTRACT call in a session.
- `scripts/highcharts-utils.js` — Chart data extraction utility. Load during pre-flight, use via `evaluate_script()` in every extraction.