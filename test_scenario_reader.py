"""检查本地示例的封装完整性和读取器的边界行为。"""

import json
import tempfile
import unittest
from pathlib import Path

from scenario_reader import iter_messages


class ScenarioTests(unittest.TestCase):
    def test_all_participant_messages_use_registry(self):
        folder = Path(__file__).with_name("examples")
        known = set(json.loads((folder / "message_types.json").read_text(encoding="utf-8")))
        examples = sorted(folder.glob("*.jsonl"))
        self.assertGreaterEqual(len(examples), 2)
        for path in examples:
            with self.subTest(filename=path.name):
                records = list(iter_messages(path, known))
                self.assertGreater(len({row["kind"] for row in records}), 1)

    def test_equal_times_keep_order_and_unknown_type_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            sample = Path(directory) / "two.jsonl"
            a = {"at": 2, "kind": "start", "record": {"item": "甲"}}
            b = {"at": 2, "kind": "start", "record": {"item": "乙"}}
            sample.write_text("\n".join(map(json.dumps, [a, b])), encoding="utf-8")
            self.assertEqual(list(iter_messages(sample, {"start"})), [a, b])
            b["kind"] = "other"
            sample.write_text("\n".join(map(json.dumps, [a, b])), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "第 2 行"):
                list(iter_messages(sample, {"start"}))

    def test_storage_message_fields(self):
        folder = Path(__file__).with_name("examples")
        known = set(json.loads((folder / "message_types.json").read_text(encoding="utf-8")))
        for example in sorted(folder.glob("*.jsonl")):
            with self.subTest(filename=example.name):
                messages = {}
                for row in iter_messages(example, known):
                    messages.setdefault(row["kind"], []).append(row["record"])
                for image in messages["image"]:
                    for block in image["blocks"]:
                        self.assertIn(int(block), range(image["size"]))
