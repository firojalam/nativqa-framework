import unittest
from nativqa.main import run_workflow


class TestWorkflow(unittest.TestCase):

    def test_workflow_execution(self):
        try:
            run_workflow()
        except Exception as e:
            self.fail(f"Workflow execution failed with error: {e}")


if __name__ == "__main__":
    unittest.main()
