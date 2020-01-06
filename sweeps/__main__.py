import argparse
import multiprocessing

from sweeps import create_rfs, delete_rfs, run_sweep, query_status

def main():
    # Define command-line parser
    sweeps = argparse.ArgumentParser(prog="sweeps",\
        description="PYTHON UTILITY FOR MANAGING PARAMETER SWEEPS")
    sweeps.add_argument('project', metavar="PROJECT",\
        help="project directory")
    subcommands = sweeps.add_subparsers(required=True, dest='subcommand',\
        title="available subcommands")
    create = subcommands.add_parser('create',\
        description="Create rfs from a sweep file")
    create.add_argument('sweep_file', metavar="SWEEP_FILE",\
        help="JSON file specifying sweep")
    delete = subcommands.add_parser('delete',\
        description="Delete rfs from a sweep file")
    delete.add_argument('sweep_file', metavar="SWEEP_FILE",\
        help="JSON file specifying sweep")
    run = subcommands.add_parser('run',\
        description="Run a parameter sweep based on existing rfs")
    run.add_argument('program', metavar="PROGRAM",\
        help="interpreter for SCRIPT")
    run.add_argument('script', metavar="SCRIPT",\
        help="location of script relative to PROJECT")
    run.add_argument('--procs', type=int, default=multiprocessing.cpu_count(),\
        help="number of processes to use")
    run.add_argument('--sweep_file', metavar="FILE",\
        help="restrict to rfs consistent with creation from JSON file FILE; "+
        "location relative to PROJECT")
    run.add_argument('--rerun_failed', action='store_true',\
        help="rerun failed rfs")
    run.add_argument('-y', '--yes', action='store_true',\
        help='proceed with running sweeps without confirmation')
    query = subcommands.add_parser('query',\
        description="Print sweep summary for a given script")
    query.add_argument('script', metavar="SCRIPT",\
        help="location of script relative to PROJECT")
    # Execute command
    args = sweeps.parse_args()
    if args.subcommand == 'create':
        create_rfs(args.project, args.sweep_file)
    elif args.subcommand == 'delete':
        delete_rfs(args.project, args.sweep_file)
    elif args.subcommand == 'run':
        run_sweep(args.project, args.program, args.script, args.procs,\
            args.sweep_file, args.rerun_failed, args.yes)
    elif args.subcommand == 'query':
        query_status(args.script, args.project)

if __name__ == "__main__":
    main()
