# task-matrix

**Prioritize research tasks with the Eisenhower matrix: important vs urgent, with urgency derived
automatically from due dates, so the paper and the grant (important, not urgent) don't lose to e-mail.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Academic work is dominated by urgent-but-unimportant requests while the important long-term work
(writing, thinking, learning methods) has no deadline until it suddenly does. Sorting tasks into four
quadrants makes that trade-off visible. The share of open tasks in Q2 (important, not urgent) is a simple
indicator of whether you are planning or only reacting.

## Features

- Tasks with importance flag, optional explicit urgency, due date, project, time estimate
- Urgency computed from the due date (within `--urgent-days`, default 3) when not set explicitly
- Quadrant view: Q1 do now, Q2 schedule, Q3 delegate/batch, Q4 drop; due countdowns and overdue flags
- Hour estimates per quadrant, project filter, JSON export; stats including the Q2 share
- Plain JSON storage (`~/task_matrix.json` or `$TASK_MATRIX_FILE`)

## Usage

```bash
pip install .
task-matrix add "Revise manuscript for journal" -i --due 2026-03-20 -e 6 -p paper2
task-matrix add "Answer facility survey" -u
task-matrix show
task-matrix done 3 4
task-matrix stats
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
