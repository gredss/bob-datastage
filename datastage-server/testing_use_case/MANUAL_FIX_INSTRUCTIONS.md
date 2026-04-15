# DataStage Job Fix - Manual Instructions

## Problem
The job "Employee Ranking_DATASTAGE_ZIP_IMPORT" rejects 129 out of 697 records because the `RANKING_CODE` field contains NULL values with no null handling configured.

## Solution: Update SQL Query in DataStage UI

Follow these steps to fix the issue directly in DataStage:

### Step 1: Open the Job
1. Log into IBM DataStage web interface
2. Navigate to project: **DataStage Level 3**
3. Open the flow: **Employee Ranking_DATASTAGE_ZIP_IMPORT**

### Step 2: Edit the RANKING_RESULTS_1 Stage
1. Double-click on the **RANKING_RESULTS_1** stage (the second Db2 Warehouse connector)
2. Go to the **Properties** tab
3. Find the **Select Statement** property

### Step 3: Update the SQL Query

**Find this line in the SQL:**
```sql
SELECT EMP.EMPLOYEE_CODE, RANKING_CODE
```

**Replace it with:**
```sql
SELECT EMP.EMPLOYEE_CODE, COALESCE(RANKING_CODE, 0) AS RANKING_CODE
```

**Complete Updated SQL Query:**
```sql
(SELECT EMP.EMPLOYEE_CODE, COALESCE(RANKING_CODE, 0) AS RANKING_CODE

FROM EMPLOYEE.EMPLOYEE EMP LEFT OUTER JOIN

(SELECT RK.*

FROM EMPLOYEE.RANKING_RESULTS RK,

(SELECT TB0.EMPLOYEE_CODE,

MAX(TB0.RANKING_DATE) RANKING_DATE

FROM EMPLOYEE.RANKING_RESULTS TB0

WHERE RANKING_DATE < '#End_Year#-01-01 00:00:00'

GROUP BY TB0.EMPLOYEE_CODE

) TB1

WHERE RK.EMPLOYEE_CODE = TB1.EMPLOYEE_CODE

AND RK.RANKING_DATE = TB1.RANKING_DATE) RK1

ON EMP.EMPLOYEE_CODE = RK1.EMPLOYEE_CODE

)
```

### Step 4: Save and Compile
1. Click **OK** to close the stage properties
2. Click **Save** to save the flow
3. Click **Compile** to compile the job

### Step 5: Test the Job
1. Run the job
2. Verify in the logs that all 697 records export successfully (0 rejected)
3. Check the output CSV - employees without ranking data will have RANKING_CODE = 0

## What This Fix Does
- `COALESCE(RANKING_CODE, 0)` returns the actual RANKING_CODE value if it exists
- If RANKING_CODE is NULL (employee has no ranking), it returns 0 instead
- This ensures all records can be exported without rejection

## Expected Results
- **Before Fix:** 568 records exported, 129 rejected
- **After Fix:** 697 records exported, 0 rejected
- Job status: **Finished** (no warnings)

## Alternative Default Values
If you prefer a different default value instead of 0, you can use:
- `-1` for "no ranking": `COALESCE(RANKING_CODE, -1)`
- `99` for "unranked": `COALESCE(RANKING_CODE, 99)`
- `NULL` string: `COALESCE(CAST(RANKING_CODE AS VARCHAR(10)), 'N/A')` (requires changing column type)

## Why Direct Export/Import Failed
DataStage export files contain complex metadata and internal references. Modifying the JSON directly can cause:
- Internal index mismatches
- Metadata inconsistencies
- Runtime errors like "Internal Error: (minIndex < m_outputLinkObjArraySize)"

**Manual editing in the UI is the safest approach** as DataStage automatically maintains all internal references and metadata.

---
**Issue Date:** 2026-04-13  
**Job Name:** Employee Ranking_DATASTAGE_ZIP_IMPORT.DataStage job  
**Stage to Modify:** RANKING_RESULTS_1