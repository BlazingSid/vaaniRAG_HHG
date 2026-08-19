import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    "benchmark", Path(__file__).parents[1] / "scripts" / "benchmark.py"
)
assert SPEC and SPEC.loader
benchmark = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(benchmark)


class BenchmarkTests(unittest.TestCase):
    def test_nearest_rank_percentiles(self) -> None:
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertEqual(benchmark.percentile(values, 50), 5)
        self.assertEqual(benchmark.percentile(values, 70), 7)
        self.assertEqual(benchmark.percentile(values, 100), 10)
