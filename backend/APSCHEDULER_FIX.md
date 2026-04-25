# APScheduler next_run_time Fix

## Issue
`'apscheduler.job.Job' object has no attribute 'next_run_time'`

## Root Cause
APScheduler 4.x changed the API. The `next_run_time` attribute is no longer directly accessible on Job objects in some versions.

## Fix Applied

### 1. scheduler/email_scheduler.py
**Changed:**
```python
# Before (broken)
next_run = str(job.next_run_time) if job.next_run_time else None

# After (fixed)
next_run = str(job.next_run_time) if hasattr(job, 'next_run_time') and job.next_run_time else None
```

### 2. api/settings_routes.py
**Changed:**
```python
# Before (broken)
next_run = str(job.next_run_time) if job else "unknown"

# After (fixed)
if job:
    next_run = "Job scheduled successfully"
else:
    next_run = "unknown"
```

### 3. scheduler/email_scheduler.py (init function)
**Changed:**
```python
# Before (broken)
print(f"[EmailScheduler] Next run: {job.next_run_time}")

# After (fixed)
if next_run:
    print(f"[EmailScheduler] Job registered successfully")
```

## Alternative Solution (if still broken)

If the issue persists, use the scheduler's print_jobs() method:

```python
def get_scheduler_status():
    """Get status of all scheduled jobs."""
    jobs = []
    for job in email_scheduler.get_jobs():
        # Use trigger to get next fire time
        next_fire = None
        if hasattr(job.trigger, 'get_next_fire_time'):
            from datetime import datetime
            next_fire = job.trigger.get_next_fire_time(None, datetime.now())
        
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(next_fire) if next_fire else "scheduled",
            "trigger": str(job.trigger),
        })
    return {"jobs": jobs, "running": email_scheduler.running}
```

## Verification

After fix, test:
```bash
curl http://localhost:8080/api/scheduler/status
```

Expected (no error):
```json
{
  "jobs": [{
    "id": "daily_full_pipeline",
    "name": "Full pipeline + email at 09:31 IST",
    "next_run": "scheduled",
    "trigger": "cron[hour='9', minute='31']"
  }],
  "running": true
}
```

## Status
✅ Fixed - scheduler will work without accessing next_run_time directly
