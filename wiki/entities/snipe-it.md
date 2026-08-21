# Snipe-IT Asset Management

**Status**: reviewed (comparison with QLTB MEIMS)

## Overview
- **Source**: https://github.com/grokability/snipe-it
- **Framework**: Laravel 12 (PHP)
- **Database**: MySQL/PostgreSQL
- **Deploy**: Docker image available (`snipe/snipe-it`)
- **License**: GPL v2

## QLTB Integration Potential

### Compatible (reuse patterns for QLTB MEIMS)
- **Asset entity model**: serial, asset_tag, purchase_date, warranty tracking
- **Maintenance entity**: separate table with asset→maintenance relations
- **Depreciation model**: linked via asset→model→depreciation
- **Assignment/Checkout model**: who has which asset, when, acceptance records
- **Categories/Manufacturers/Departments/Locations**: taxonomy pattern reusable

### Missing for Biomedical Devices (gaps to fill in QLTB)
- ❌ Calibration traceability (due dates, certificates, traceability chain) 
- ❌ Risk class (IEC 60601: risk class B, C, or D)
- ❌ MTBF / MTTR (reliability metrics)
- ❌ PM compliance tracking (ISO 13485:2016 7.5.4 — planned maintenance)
- ❌ Regulatory evidence linkage (attach ISO 13485, FDA 21 CFR Part 820 records)

## Suggested QLTB Extensions
1. Extend `Asset` model → add: `calibration_due`, `calibration_certificate_path`, `risk_class`, `IEC_standard`
2. Extend `Maintenance` → link to PM schedule with recurrence pattern (cron-like)
3. Add `MTBF` computed field = `total_uptime_hours / number_of_failures`
4. Add `PM schedule` model with `next_due_date`, `compliance_status`

## References
- [[snipe-it-architecture]]
- [[mri_1_5t_power_loss_troubleshooting]]
