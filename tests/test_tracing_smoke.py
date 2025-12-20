import os
import subprocess
import sys
import time


def test_tracing_smoke():
    # Run the smoke script and assert it exits with success code 0
    script = os.path.join(os.getcwd(), "scripts", "tracing_smoke_test.sh")
    assert os.path.exists(script)

    proc = subprocess.run([script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=os.environ.copy())
    print(proc.stdout)
    # Accept success (0) or warning code 4 (span delayed but collector reachable)
    assert proc.returncode in (0, 4)
