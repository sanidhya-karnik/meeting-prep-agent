# CRM Dataset Enhancement Review Pack

This review pack proposes a cohesive, standardized enhancement to the current mimicked Salesforce-like dataset in `data/postgres/init.sql`.

No production schema or seed file has been modified in this step. This is a review artifact only.

## 1) Goal

Make the CRM dataset more useful for meeting-prep workflows by adding:

- richer account context (firmographics),
- product-level opportunity context,
- sales team hierarchy,
- stronger pipeline analytics and health signals,
- clear data quality standardization rules.

## 2) Current Dataset (Before)

Current tables:

- `clients`
- `contacts`
- `deals`
- `activities`
- `health_metrics`

Current strengths:

- Good account + contact + activity narrative for briefings.
- Enough fields for basic opportunity status.

Current gaps:

- No formal product catalog or product-to-deal link.
- `deals.owner` is free text (not standardized).
- Limited firmographics for account profiling.
- No stage history and limited performance metrics.
- No built-in data quality metadata.

## 3) External CRM Dataset Inputs Assessed

Files reviewed from `/Users/angella/Downloads/CRM+Sales+Opportunities`:

- `accounts.csv` (firmographics)
- `products.csv` (product catalog)
- `sales_teams.csv` (rep hierarchy and regions)
- `sales_pipeline.csv` (opportunity lifecycle and value)

Profiling highlights:

- Pipeline rows: 8,800 opportunities
- Stages: Prospecting, Engaging, Won, Lost
- Closed opportunities (Won/Lost): 6,711
- Win rate among closed: 63.15%
- Data quality mismatches:
  - blank account value in 1,425 rows,
  - `GTXPro` in pipeline vs `GTX Pro` in product table (1,480 rows),
  - misspelled industry value `technolgy`.

## 4) Proposed Enhanced Data Model (After)

### A) Enrich `clients`

Add:

- `year_established`
- `annual_revenue_musd`
- `employee_count`
- `parent_company`
- `data_quality_flag`

Why:

- Improves account prep with size, maturity, ownership context.

### B) Add `sales_reps` table

Add a normalized owner dimension:

- `rep_name`
- `manager_name`
- `regional_office`

Why:

- Supports territory and manager-based coaching/performance views.

### C) Add `products` table

Add product catalog:

- `name`
- `series`
- `list_price`
- `is_active`

Why:

- Enables product-level insights and cleaner pricing context.

### D) Enhance `deals`

Add:

- `external_opportunity_id`
- `product_id` (FK to products)
- `owner_id` (FK to sales_reps)
- `engage_date`
- `list_price_snapshot`

Why:

- Creates a robust bridge between opportunities, products, and sales team.

### E) Add `deal_stage_history`

Track stage transitions:

- `deal_id`
- `stage`
- `entered_at`
- `exited_at`
- `source_system`

Why:

- Enables cycle-time and stalled-opportunity analytics.

### F) Extend `health_metrics`

Add derived metrics:

- `win_rate_90d`
- `avg_cycle_days_90d`
- `avg_closed_value_90d`
- `open_pipeline_value`

Why:

- Turns health from static status to decision-ready KPI view.

## 5) Standardization Rules (Critical)

Apply before loading:

1. Product canonicalization:
   - `GTXPro` -> `GTX Pro`
2. Industry normalization:
   - `technolgy` -> `technology`
3. Account handling:
   - blank `account` values map to `Unknown Account` or nullable client with `data_quality_flag='missing_account'`
4. Units:
   - `revenue` explicitly treated as "millions of USD" and mapped to `annual_revenue_musd`.
5. Stage mapping:
   - Keep canonical stages in `deals.stage`: Prospecting, Engaging, Won, Lost.

## 6) Before vs After Snapshot

- Before:
  - 5 base tables
  - no product dimension
  - no sales hierarchy table
  - no stage history
  - limited health KPIs
- After (proposed):
  - 8 base tables (`+ sales_reps`, `+ products`, `+ deal_stage_history`)
  - expanded account intelligence
  - normalized owner/product keys
  - richer pipeline analytics
  - stronger data quality controls

Detailed dictionaries are provided in:

- `data/documents/crm_dataset_before_current.csv`
- `data/documents/crm_dataset_after_proposed.csv`

## 7) Implementation Plan (Not Yet Executed)

Phase 1: Schema migration in `init.sql` (additive, backward-compatible first)

Phase 2: Data staging + cleaning pipeline

Phase 3: Load dimensions (`sales_reps`, `products`, enriched `clients`)

Phase 4: Load opportunities into `deals` and optionally `deal_stage_history`

Phase 5: Update CRM views for briefing use case

Phase 6: QA checks (row counts, FK integrity, stage/value consistency)

## 8) Recommendation

Proceed with the proposed schema enhancements in a review branch after approval of this pack. Start with additive columns/tables and dual-write support to avoid breaking existing agents.
