"""Supervise the single assigned model process with a conservative GPU-time upper bound."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
deadline = datetime(2026, 9, 21, 19, 55, 27, tzinfo=timezone.utc).timestamp()
budget_file = ROOT / 'logs/model-budget.json'
if budget_file.exists():
    raise SystemExit('Single attempt already recorded; no automatic retry authorized.')
remaining = deadline - time.time() - 180
limit = min(300, remaining)
if limit <= 0:
    raise SystemExit('Wall-clock budget leaves no time for inference and cleanup.')
record = {'started_utc':datetime.now(timezone.utc).isoformat(), 'timeout_s':limit,
          'accounting':'entire inference child process wall time is a conservative upper bound on model GPU activity, including failed loading/inference; no second attempt',
          'status':'started'}
budget_file.write_text(json.dumps(record,indent=2))
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
started = time.perf_counter()
with (ROOT/'logs/run-518.log').open('w') as log:
    child = subprocess.Popen([sys.executable,'-u',str(ROOT/'run_tum.py'),'--output','run-518'],
                             stdout=log,stderr=subprocess.STDOUT,env=env)
    record['pid'] = child.pid
    try:
        record['exit_code'] = child.wait(timeout=limit)
        record['status'] = 'completed' if record['exit_code'] == 0 else 'failed'
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True)
        child.wait(timeout=15)
        record['status'] = 'budget-timeout'
    finally:
        record['child_process_wall_s'] = time.perf_counter()-started
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
        budget_file.write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
raise SystemExit(0 if record['status'] == 'completed' else 1)
