"""读取存储端与调用方的仿真消息，保持到达顺序。"""

import argparse
import json
from collections import Counter
from pathlib import Path


def iter_messages(path, supported):
    previous = -1
    with path.open(encoding="utf-8") as source:
        for line_number, raw in enumerate(source, 1):
            try:
                row = json.loads(raw)
                if not isinstance(row, dict) or set(row) != {"at", "kind", "record"}:
                    raise ValueError("消息需要 at、kind 和 record 字段")
                timestamp = row["at"]
                if type(timestamp) is not int or timestamp < 0 or timestamp < previous:
                    raise ValueError("到达秒点必须为非负整数，且不能倒退")
                if not isinstance(row["kind"], str) or row["kind"] not in supported:
                    raise ValueError("未登记的消息名称")
                if not isinstance(row["record"], dict):
                    raise ValueError("record 应为对象")
            except ValueError as error:
                raise ValueError(f"{path.name} 第 {line_number} 行：{error}") from error
            previous = timestamp
            yield row


def summarize(directory):
    supported = set(json.loads((directory / "message_types.json").read_text(encoding="utf-8")))
    paths = sorted(directory.glob("*.jsonl"))
    if not paths:
        raise ValueError("没有可读取的场景")
    for path in paths:
        counts = Counter()
        for message in iter_messages(path, supported):
            counts[message["kind"]] += 1
        if not counts:
            raise ValueError(f"{path.name} 没有消息")
        breakdown = "，".join(f"{kind} {counts[kind]}" for kind in sorted(counts))
        print(f"{path.name}　{sum(counts.values())} 条　{breakdown}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="清点存储操作记录记录")
    parser.add_argument("directory", type=Path)
    summarize(parser.parse_args().directory)
