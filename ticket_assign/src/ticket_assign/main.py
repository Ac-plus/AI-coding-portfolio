from __future__ import annotations

import argparse
import json
from pathlib import Path

from ticket_assign.config.scenario_loader import load_scenario
from ticket_assign.simulator.engine import SimulationEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行客服工单分配模拟")
    parser.add_argument("scenario", type=Path, help="场景配置文件路径")
    parser.add_argument(
        "--dispatcher",
        default="fifo",
        help="分配策略，可选值：fifo、priority_first、least_loaded、balanced",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="以缩进 JSON 打印结果，便于阅读",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    scenario = load_scenario(args.scenario)
    engine = SimulationEngine.from_scenario(scenario, dispatcher_name=args.dispatcher)
    result = engine.run()
    if args.pretty:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    print(json.dumps(result.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
