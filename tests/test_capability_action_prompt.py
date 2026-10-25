import unittest
import worker

class CapabilityActionPromptTests(unittest.TestCase):
    def test_prompt_advertises_capability_registry_action(self):
        prompt = worker.build_prompt({"history": [], "cycle": 0})
        self.assertIn("inspect_capability_registry", str(prompt))

if __name__ == "__main__":
    unittest.main()
