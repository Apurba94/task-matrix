"""Tasks are classified by importance and urgency; urgency can be derived from due dates."""
import datetime as dt
import json
import os

QUADRANTS = {
    1: ("Do now", "urgent and important"),
    2: ("Schedule", "important, not urgent"),
    3: ("Delegate / batch", "urgent, not important"),
    4: ("Drop", "neither urgent nor important"),
}


def quadrant(important, urgent):
    return {(True, True): 1, (True, False): 2, (False, True): 3, (False, False): 4}[(bool(important), bool(urgent))]


class TaskBoard:
    def __init__(self, path=None, today=None, urgent_days=3):
        self.path = path or os.environ.get("TASK_MATRIX_FILE", os.path.join(os.path.expanduser("~"), "task_matrix.json"))
        self.today = today or dt.date.today()
        self.urgent_days = urgent_days
        self.data = {"next_id": 1, "tasks": []}
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as fh:
                self.data = json.load(fh)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=1)

    def add(self, title, important=False, urgent=None, due=None, project="", estimate_h=None):
        if due:
            dt.date.fromisoformat(due)
        t = {"id": self.data["next_id"], "title": title, "important": bool(important), "urgent": urgent,
             "due": due, "project": project, "estimate_h": estimate_h, "done": False,
             "created": self.today.isoformat()}
        self.data["next_id"] += 1
        self.data["tasks"].append(t)
        self.save()
        return t

    def _get(self, tid):
        for t in self.data["tasks"]:
            if t["id"] == tid:
                return t
        raise KeyError(tid)

    def is_urgent(self, t):
        """Explicit flag wins; otherwise urgent when due within `urgent_days` (or overdue)."""
        if t["urgent"] is not None:
            return t["urgent"]
        if t["due"]:
            return (dt.date.fromisoformat(t["due"]) - self.today).days <= self.urgent_days
        return False

    def quadrant_of(self, t):
        return quadrant(t["important"], self.is_urgent(t))

    def update(self, tid, **fields):
        t = self._get(tid)
        for k, v in fields.items():
            if k not in ("title", "important", "urgent", "due", "project", "estimate_h", "done"):
                raise ValueError("cannot update %r" % k)
            t[k] = v
        if fields.get("done"):
            t["completed"] = self.today.isoformat()
        self.save()
        return t

    def remove(self, tid):
        self.data["tasks"].remove(self._get(tid))
        self.save()

    def matrix(self, project=None, include_done=False):
        m = {q: [] for q in QUADRANTS}
        for t in self.data["tasks"]:
            if (t["done"] and not include_done) or (project and t["project"] != project):
                continue
            m[self.quadrant_of(t)].append(t)
        for q in m:
            m[q].sort(key=lambda t: (t["due"] or "9999-12-31", t["id"]))
        return m

    def stats(self):
        done = [t for t in self.data["tasks"] if t["done"]]
        by_q = {q: 0 for q in QUADRANTS}
        for t in done:
            by_q[quadrant(t["important"], bool(t["urgent"]) if t["urgent"] is not None else False)] += 1
        overdue = [t for t in self.data["tasks"] if not t["done"] and t["due"] and t["due"] < self.today.isoformat()]
        return {"open": len(self.data["tasks"]) - len(done), "done": len(done), "overdue": len(overdue),
                "q2_share_of_open": round(100 * len(self.matrix()[2]) / max(1, len(self.data["tasks"]) - len(done)))}


def render(matrix, today, width=38):
    out = []
    for q, (name, desc) in QUADRANTS.items():
        tasks = matrix[q]
        hours = sum(t["estimate_h"] or 0 for t in tasks)
        out.append("Q%d %s (%s) - %d task(s)%s" % (q, name.upper(), desc, len(tasks), ", ~%gh" % hours if hours else ""))
        for t in tasks:
            due = ""
            if t["due"]:
                days = (dt.date.fromisoformat(t["due"]) - today).days
                due = " [due %s, %s]" % (t["due"], "%dd overdue" % -days if days < 0 else "in %dd" % days)
            out.append("   #%-3d %s%s%s" % (t["id"], t["title"][:width], due, " (%s)" % t["project"] if t["project"] else ""))
        out.append("")
    return "\n".join(out)
