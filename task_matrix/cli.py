"""Command-line interface for task-matrix."""
import argparse
import json

from .core import TaskBoard, render


def main(argv=None, today=None):
    ap = argparse.ArgumentParser(prog="task-matrix", description="Eisenhower matrix for research tasks.")
    ap.add_argument("--file", help="JSON store (default ~/task_matrix.json or $TASK_MATRIX_FILE)")
    ap.add_argument("--urgent-days", type=int, default=3, help="due within N days counts as urgent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("title")
    a.add_argument("-i", "--important", action="store_true")
    a.add_argument("-u", "--urgent", action="store_true", help="force urgent (otherwise derived from --due)")
    a.add_argument("--due", help="YYYY-MM-DD")
    a.add_argument("-p", "--project", default="")
    a.add_argument("-e", "--estimate", type=float, help="hours")
    sh = sub.add_parser("show")
    sh.add_argument("-p", "--project")
    sh.add_argument("--json", action="store_true")
    d = sub.add_parser("done")
    d.add_argument("ids", type=int, nargs="+")
    r = sub.add_parser("rm")
    r.add_argument("id", type=int)
    sub.add_parser("stats")
    args = ap.parse_args(argv)
    board = TaskBoard(args.file, today, args.urgent_days)
    try:
        if args.cmd == "add":
            t = board.add(args.title, args.important, True if args.urgent else None, args.due, args.project, args.estimate)
            print("#%d -> Q%d" % (t["id"], board.quadrant_of(t)))
        elif args.cmd == "show":
            m = board.matrix(args.project)
            print(json.dumps(m, indent=1) if args.json else render(m, board.today))
        elif args.cmd == "done":
            for i in args.ids:
                board.update(i, done=True)
        elif args.cmd == "rm":
            board.remove(args.id)
        else:
            s = board.stats()
            print("%d open, %d done, %d overdue; %d%% of open tasks are important-not-urgent (Q2)" % (
                s["open"], s["done"], s["overdue"], s["q2_share_of_open"]))
    except (KeyError, ValueError) as exc:
        print("error: %s" % exc)
        return 1
    return 0
