import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from nativqa.nativqa_framework import run_nativqa


class TestNativQA(unittest.TestCase):
    @classmethod
    def setUpClass (cls):
        cls.result_dir = TemporaryDirectory()
        cls.result_path = cls.result_dir.name
        cls.input_file = 'tests/data/test_query.csv'
        result_path = Path(cls.result_path) / cls.input_file
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.touch(exist_ok=True)

    def test_scrape(self):
        try:
            args = {
                "input_file": self.input_file,
                "location": 'Doha, Qatar',
                "gl": 'qa',
                "multiple_country": None,
                "result_dir": self.result_path,
                "env": 'tests/envs/api_key.env',
                "n_iter": 3
            }
            run_nativqa(**args)
        except Exception as e:
            self.fail(f"scrape execution failed with error: {e}")

    @classmethod
    def tearDownClass(cls):
        cls.result_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
