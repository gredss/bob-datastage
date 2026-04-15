# DataStage Job Fix - Employee Ranking Import

## Problem Identified
The DataStage job "Employee Ranking_DATASTAGE_ZIP_IMPORT" was completing with warnings, rejecting 129 out of 697 records during export.

### Root Cause
- The job performs a LEFT OUTER JOIN between employee data and ranking results
- When employees don't have ranking data, the `RANKING_CODE` field contains NULL values
- The Sequential File output stage had no null handling configured, causing export failures

### Error Messages from Logs
```
##W IIS-DSEE-TFIG-00208 Field "RANKING_CODE" is null but no null export handling is defined
##W IIS-DSEE-TOIX-00008 Export was unsuccessful at record 1; continuing.
```

## Solution Applied
Modified the `RANKING_RESULTS_1` connector SQL query to handle NULL values at the source using COALESCE function.

### Change Made
**Original SQL:**
```sql
SELECT EMP.EMPLOYEE_CODE, RANKING_CODE
FROM EMPLOYEE.EMPLOYEE EMP LEFT OUTER JOIN ...
```

**Fixed SQL:**
```sql
SELECT EMP.EMPLOYEE_CODE, COALESCE(RANKING_CODE, 0) AS RANKING_CODE
FROM EMPLOYEE.EMPLOYEE EMP LEFT OUTER JOIN ...
```

### What This Does
- `COALESCE(RANKING_CODE, 0)` returns the RANKING_CODE value if it's not NULL
- If RANKING_CODE is NULL, it returns 0 instead
- This ensures all records can be exported successfully without rejection

## Files Modified
- `data_intg_flow/Employee Ranking_DATASTAGE_ZIP_IMPORT.json` - Updated SQL query in RANKING_RESULTS_1 stage

## Import Instructions
1. Open IBM DataStage web interface
2. Navigate to your project: "DataStage Level 3"
3. Go to Assets > Import
4. Upload the file: `Employee_Ranking_DATASTAGE_ZIP_IMPORT_FIXED.zip`
5. Select "Replace" option if the job already exists
6. Complete the import process

## Testing
After importing, run the job and verify:
- All 697 records should export successfully (0 rejected)
- Employees without ranking data will have RANKING_CODE = 0 in the output CSV
- Job should complete with status "Finished" (no warnings)

## Alternative Solutions Considered
1. **Add null handling to Sequential File stage** - Would require manual configuration in UI
2. **Add Transformer stage** - Would add unnecessary complexity to the flow
3. **Modify SQL with COALESCE** - ✅ **Selected** - Cleanest solution, fixes at source

## Expected Results
- **Before Fix:** 568 records exported, 129 rejected
- **After Fix:** 697 records exported, 0 rejected

## Notes
- The value `0` was chosen as the default for NULL RANKING_CODE
- If you prefer a different default (e.g., -1, 99, or 'N/A'), you can modify the COALESCE function accordingly
- The fix maintains data integrity while ensuring all records are exported

---
**Fix Date:** 2026-04-13  
**Fixed By:** Bob (AI Assistant)  
**Job Name:** Employee Ranking_DATASTAGE_ZIP_IMPORT.DataStage job