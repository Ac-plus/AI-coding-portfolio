from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


class BenchmarkReportTest(unittest.TestCase):
    def test_benchmark_script_generates_report_and_metrics(self) -> None:
        root = Path(__file__).resolve().parents[2]
        completed = subprocess.run(
            [sys.executable, "scripts/run_benchmark.py"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src"},
        )
        payload = json.loads(completed.stdout.strip())
        report_path = Path(payload["report"])
        metrics_path = Path(payload["metrics"])

        self.assertTrue(report_path.exists())
        self.assertTrue(metrics_path.exists())

        report_text = report_path.read_text(encoding="utf-8")
        self.assertIn("## 1. 覆盖范围", report_text)
        self.assertIn("### 5.2. 高峰场景测试", report_text)
        self.assertIn("### 5.5. 结果可复现测试", report_text)
        self.assertIn("| README 指标要求 | 报告是否覆盖 | 对应输出位置 |", report_text)
        self.assertIn("| 指标类别 | 指标名称 | 数值 |", report_text)
        self.assertIn("P1 工单平均等待时长", report_text)
        self.assertIn("技能不匹配分配次数", report_text)


if __name__ == "__main__":
    unittest.main()
