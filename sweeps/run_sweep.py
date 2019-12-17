import argparse
import os, os.path as path, shutil
import signal
import subprocess, multiprocessing

from .sweep_utils import get_timestamp, asheader, write, get_script_id
from .sweep_utils import Status, collect_rf_status, generate_status
from .setup_sweep import read_sweep

def run_sweep(project, prog, script, num_procs, sweep=None, rerun_failed=False):
    timestamp = get_timestamp()
    # Determine status of all requested rfs
    rf_status = collect_rf_status(script, project)
    if sweep is not None:
        sweep_file = path.join(project,sweep)
        rfs = [rf for rf,_ in read_sweep(sweep_file)]
        for status in Status:
            rf_status[status].intersection_update(rfs)
    queued_rfs = set(rf_status[Status.NEW])
    if rerun_failed:
        queued_rfs.update(rf_status[Status.FAILED])
    # Write summary of rfs status to file
    run = timestamp+'.run'
    run_file = path.join(project,run)
    script_id = get_script_id(script,project)
    with open(run_file, 'a') as file:
        write(file, "# RUN FILE FOR SWEEP GENERATED AT " + timestamp)
        write(file, "# script: " + script_id)
        write(file, "# rerun_failed: " + str(rerun_failed))
        write(file, "# rfs: " + (sweep if sweep else "All"))
        write(file, asheader("REQUESTED RFs QUEUED TO RUN", "# "))
        for rf in sorted(queued_rfs):
            write(file, rf)
        write(file, asheader("REQUESTED RFs WITH INVALID STATUS", "## "))
        for rf in sorted(rf_status[Status.INVALID]):
            write(file, "## " + rf)
        write(file, asheader("REQUESTED RFs QUEUED OR RUNNING", "### "))
        for rf in sorted(rf_status[Status.QUEUED]):
            write(file, "### " + rf)
        for rf in sorted(rf_status[Status.RUNNING]):
            write(file, "### " + rf)
    # Prompt for approval
    if rf_status[Status.INVALID]:
        print("Warning: Found rfs with status INVALID (ignored)")
    if rf_status[Status.RUNNING] or rf_status[Status.QUEUED]:
        print("Warning: Found rfs with status QUEUED or RUNNING (ignored)")
    approval = 'y'
    if not approval == 'y':
        return print("Aborting sweep.")
    # Define signal handlers
    def handle_signal(rc, *args):
        if rc == signal.SIGINT:
            print("\nSweep interrupted", end="")
        else:
            print("Sweep received external SIGNAL "+str(rc), end="")
        print(": Terminating processes.")
        pool.terminate()
        pool.join()
        for rf in queued_rfs:
            with open(path.join(project,'rfs',rf,'status.txt'), 'a') as status:
                write(status, generate_status("  KILLED",script_id))
        raise SystemExit(rc)
    signal.signal(signal.SIGQUIT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    # Copy to history
    os.rename(run_file, path.join(project,'history',run))
    if sweep is not None:
        os.rename(sweep_file, path.join(project,'history',sweep))
    shutil.copyfile(path.join(project,'bin',script),\
        path.join(project,'history',timestamp+'.script'))
    for rf in queued_rfs:
        with open(path.join(project,'rfs',rf,'status.txt'), 'a') as status:
            write(status, generate_status("  QUEUED",script_id))
    # Start the sweep
    pool = multiprocessing.Pool(processes=num_procs)
    args = [(project, prog, script, rf) for rf in queued_rfs]
    pool.imap_unordered(run_rf, args, chunksize=1)
    pool.close()
    # Wait for sweep to finish or quit
    #print("Sweep started. Press CTRL+C to interrupt.")
    pool.join()
    print("Sweep completed.")

def run_rf(args):
    project, prog, script, rf = args
    rf_path = path.join(project, 'rfs', rf)
    script_path = path.join(project, 'bin', script)
    script_id = get_script_id(script, project)
    # Open log and status files
    log = open(path.join(rf_path,'log.txt'), 'a')
    status = open(path.join(rf_path,'status.txt'), 'a')
    write(log, asheader("LOG FILE OPENED "+get_timestamp()))
    # Define signal handlers
    def handle_signal(rc, *args):
        write(log, "SIGNAL "+str(rc)+" RECEIVED: TERMINATING SCRIPT")
        process.terminate()
        raise SystemExit(rc)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, handle_signal)
    # Run the script
    process = subprocess.Popen([prog, script_path, rf_path],\
        stdout=log, stderr=subprocess.STDOUT)
    write(status, generate_status(" STARTED",script_id))
    try:
        rc = process.wait()
    except SystemExit as e:
        rc = e.code
        raise e
    finally:
        if rc == 0:
            write(status, generate_status("FINISHED",script_id))
        else:
            write(log, "SCRIPT RETURNED WITH EXIT CODE "+str(rc))
            write(status, generate_status("  FAILED",script_id))
        write(log, asheader("LOG FILE CLOSED "+get_timestamp()))
        log.close()
        status.close()
