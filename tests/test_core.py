import datetime as dt
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from task_matrix.cli import main
from task_matrix.core import TaskBoard, quadrant, render

TODAY = dt.date(2026, 3, 4)


class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.b = TaskBoard(os.path.join(self.tmp.name, "t.json"), TODAY)

    def tearDown(self):
        self.tmp.cleanup()

    def test_quadrant_function(self):
        self.assertEqual([quadrant(i, u) for i, u in ((1, 1), (1, 0), (0, 1), (0, 0))], [1, 2, 3, 4])

    def test_urgency_from_due_date(self):
        a = self.b.add("Revise paper", important=True, due="2026-03-06")
        c = self.b.add("Write grant", important=True, due="2026-04-30")
        e = self.b.add("Reply to vendor", urgent=True)
        f = self.b.add("Reorganize bookmarks")
        self.assertEqual([self.b.quadrant_of(t) for t in (a, c, e, f)], [1, 2, 3, 4])

    def test_update_done_and_persist(self):
        t = self.b.add("Review for journal", important=True, due="2026-03-01")
        self.b.update(t["id"], done=True)
        again = TaskBoard(self.b.path, TODAY)
        self.assertEqual(again.matrix()[1], [])
        self.assertEqual(len(again.matrix(include_done=True)[1]), 1)
        with self.assertRaises(ValueError):
            self.b.update(t["id"], colour="red")
        with self.assertRaises(KeyError):
            self.b.remove(99)

    def test_render_and_stats(self):
        self.b.add("Old task", important=True, due="2026-03-01", estimate_h=2)
        self.b.add("Plan study", important=True, project="p1")
        text = render(self.b.matrix(), TODAY)
        self.assertIn("Q1 DO NOW", text)
        self.assertIn("3d overdue", text)
        self.assertIn("~2h", text)
        s = self.b.stats()
        self.assertEqual((s["open"], s["overdue"], s["q2_share_of_open"]), (2, 1, 50))

    def test_cli(self):
        with redirect_stdout(io.StringIO()) as buf:
            main(["--file", self.b.path, "add", "Submit abstract", "-i", "--due", "2026-03-05"], today=TODAY)
            main(["--file", self.b.path, "show"], today=TODAY)
        self.assertIn("#1 -> Q1", buf.getvalue())
        self.assertIn("Submit abstract", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
