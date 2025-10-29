from pathlib import Path
import subprocess, datetime
from typing import Tuple, List

def run_robot_and_get_report(gen_dir: Path, report_dir: Path) -> Tuple[Path, List[str], str]:
    """
    Run Robot Framework tests and generate timestamped report.
    
    Returns:
        Tuple of (output_directory, logs, timestamp)
    """
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = report_dir / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    # Run Robot Framework on generated dir
    cmd = ["robot", "--outputdir", str(out_dir), str(gen_dir)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    logs = []
    if proc.stdout:
        for line in proc.stdout:
            logs.append(line.rstrip())
    proc.wait()
    return out_dir, logs, ts
