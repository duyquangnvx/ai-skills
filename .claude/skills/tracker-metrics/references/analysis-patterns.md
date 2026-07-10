# Analysis Patterns

Patterns for analyzing metrics data extracted from the tracker. Use these when interpreting Highcharts data to answer user questions, build reports, or diagnose issues.

## Metric relationship graph

This is the core knowledge structure. When one metric shows an anomaly, follow the graph to investigate related metrics.

```
A1 (Daily Active Users)
├── drops → check N1, Churn Rate, Quality Errors, CCU
├── spikes → check marketing campaigns, events, game updates
└── related pages: Account > New & Active

N1 (New Users)
├── drops → check Install Quality, marketing spend, store ranking
├── spikes → check campaign launches, featuring
└── related pages: Account > New & Active, Install > Install Quality

Revenue (Gross/Net)
├── drops → check A1, Paying Rate, ARPU, ARPPU
├── spikes → check special offers, events, new IAP items
└── related pages: Cash > Daily, Cash > Monthly

Churn Rate
├── increases → check Quality Errors, game updates (GameChange), A1 trend
├── segments: Churn1 (1-day), Churn3, Churn7, Churn15, Churn30
└── related pages: Account > New & Active

Retention Rate
├── drops → check game quality, onboarding changes, server issues
├── segments: RR1, RR3, RR7, RR15, RR30
└── related pages: Account > New & Active

JS Errors / Quality Errors
├── spikes → check recent game updates (GameChange), OS version distribution
├── correlate with: A1 drops, Churn increases, Loading Fail
└── related pages: Quality > JS Error, Quality > Error Overview, Quality > Loading Fail

CCU (Concurrent Users)
├── drops → check server issues, A1 trend, scheduled maintenance
├── hourly patterns: distinguish time-of-day patterns from real drops
└── related pages: Quality > CCU
```

## Analysis techniques

### Trend detection

Compare current period vs previous period:

```
Given: data = [49, 38, 43, 36, 44, 45, 37, 41]
Calculate:
  - Mean: 41.6
  - Recent mean (last 3): 40.7
  - Previous mean (first 3): 43.3
  - Trend: declining (-6%)
```

Report trends as:
- **Stable**: variance < 10% from mean
- **Declining**: recent average > 10% below overall mean
- **Growing**: recent average > 10% above overall mean
- **Volatile**: high variance with no clear direction

### Spike/drop detection

A data point is an anomaly if it deviates significantly from neighbors:

```
Given: data = [2, 1, 1, 10, 2, 1]  (index 3 is spike)
Method: Compare each point to rolling average of neighbors
  - Point: 10, Neighbors avg: 1.5
  - Deviation: 567% → flag as spike
```

Thresholds:
- **Notable**: > 50% deviation from neighbor average
- **Significant**: > 100% deviation
- **Critical**: > 200% deviation

Always report: date, value, deviation %, and how many devices were affected (ErrorQty vs DeviceQty ratio reveals if one device is repeating errors).

### Cross-metric correlation

When investigating an anomaly, collect related metrics for the same time period and look for co-occurring changes:

```
Observation: A1 dropped 20% on 02-16
Check N1:     Normal → not an acquisition problem
Check Churn:  Churn1 spiked to 47% → users leaving
Check Errors: JS Error spiked to 10 → technical issue
Check GameChange: Update deployed 02-15 → likely cause

Diagnosis: Game update on 02-15 introduced JS errors,
           causing increased churn and A1 drop.
```

### Period comparison

For "how is this week vs last week" questions:

```
This week:  [Mon, Tue, Wed, Thu, Fri, Sat, Sun]
Last week:  [Mon, Tue, Wed, Thu, Fri, Sat, Sun]

Compare: day-by-day (same weekday) and total
Report: % change per day + total % change
Flag: any day with > 20% change
```

## Report templates

### Health report structure

```markdown
# Game Health Report: {app_name}
Period: {from} to {to}

## Executive Summary
- Overall health: [Healthy / Warning / Critical]
- Key highlights: [2-3 bullet points]

## User Metrics
- A1 (Daily Active): {value} ({trend} vs previous period)
- N1 (New Users): {value} ({trend})
- Retention (RR1/RR7): {value}%
- Churn (Churn1/Churn7): {value}%

## Revenue
- Gross Revenue: {value} VND ({trend})
- ARPU: {value} VND
- Paying Rate: {value}%

## Quality
- JS Errors: {total} (avg {daily_avg}/day)
- Top error: {description}
- CCU peak: {value}

## Anomalies & Recommendations
1. {anomaly description} → {recommended action}
```

### Diagnostic report structure

```markdown
# Diagnostic: {question}
Date investigated: {date}

## Observation
{metric} showed {anomaly type} on {date}: {value} (expected ~{expected})

## Investigation
| Related metric | Value | Normal range | Status |
|---|---|---|---|
| {metric} | {value} | {range} | Normal/Anomaly |

## Root cause
{explanation with evidence}

## Recommendations
1. {action item}
```

## Self-improvement: updating the catalog

After every analysis, consider what was learned:

### New observations to record
- "A1 for {app} typically ranges 40-60 on weekdays"
- "JS errors spike after game updates — check GameChange page"
- "Revenue drops on weekends for this app"

### New relationships discovered
- "Loading Fail correlates strongly with JS Errors for this app"
- "N1 spikes on Tuesdays (possible scheduled marketing)"

### Format for appending to catalog

Add observations under the relevant metric entry:

```markdown
## A1
...existing content...

### Observations
- [2026-02-27] Normal range for buraco_it: 40-60 weekday, 35-50 weekend
- [2026-02-27] A1 drop on 02-16 correlated with JS error spike after game update
```

This accumulated knowledge makes future analyses faster and more accurate — the agent doesn't have to re-discover the same patterns.
