from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class BenchmarkCaseResult:
    case_id: str
    title: str
    scenario: str
    dispatcher: str
    purpose: str
    steps: list[str]
    observations: list[str]
    result: dict


class ReportBuilder:
    def build_markdown(self, case_results: list[BenchmarkCaseResult], generated_at: str) -> str:
        lines: list[str] = []
        lines.append("# 客服工单自动分配系统测试报告")
        lines.append("")
        lines.append(f"- 生成时间: {generated_at}")
        lines.append(f"- 覆盖测试数: {len(case_results)}")
        lines.append("- 指标覆盖: README 第 4 节全部指标")
        lines.append("- 用例覆盖: README 第 5 节全部必做测试")
        lines.append("")
        lines.append("## 1. 覆盖范围")
        lines.append("")
        lines.append("### 1.1 指标覆盖确认")
        lines.append("")
        lines.append("| README 指标要求 | 报告是否覆盖 | 对应输出位置 |")
        lines.append("| --- | --- | --- |")
        lines.append("| P1 工单平均等待时长 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| P1 工单 P95 等待时长 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| P1 工单 SLA 达成率 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 全部工单平均等待时长 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 全部工单平均完成时长 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 工单队列平均长度 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 工单转派率 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 客服平均利用率 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 客服利用率方差 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 高峰时段系统吞吐量 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 每位客服处理工单数最大值、最小值、方差 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 最长未被处理普通工单等待时长 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 饥饿工单数 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 技能不匹配分配次数 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("| 因转派带来的额外处理成本总时长 | 是 | 各测试用例的“指标输出”表格 |")
        lines.append("")
        lines.append("### 1.2 测试场景覆盖确认")
        lines.append("")
        lines.append("| README 测试要求 | 报告是否覆盖 | 对应测试章节 |")
        lines.append("| --- | --- | --- |")
        lines.append("| 5.1 基线对比 | 是 | 5.1-A、5.1-B、5.1-C、5.1-D |")
        lines.append("| 5.2 高峰场景 | 是 | 5.2 |")
        lines.append("| 5.3 离线场景 | 是 | 5.3 |")
        lines.append("| 5.4 转派场景 | 是 | 5.4 |")
        lines.append("| 5.5 结果可复现 | 是 | 5.5 |")
        lines.append("")
        lines.append("## 2. 测试结果")
        lines.append("")

        for case in case_results:
            lines.append(f"### {case.case_id}. {case.title}")
            lines.append("")
            lines.append(f"- 场景: `{case.scenario}`")
            lines.append(f"- 策略: `{case.dispatcher}`")
            lines.append(f"- 目的: {case.purpose}")
            lines.append("- 测试步骤:")
            for step in case.steps:
                lines.append(f"  - {step}")
            lines.append("- 观察结论:")
            for item in case.observations:
                lines.append(f"  - {item}")
            lines.append("- 指标输出:")
            lines.extend(self._metrics_table(case.result["metrics"]))
            lines.append("- 结果摘要:")
            lines.extend(self._summary_table(case.result))
            lines.append("- 日志样例:")
            lines.extend(self._log_sample_table(case.result["logs"]))
            lines.append("")

        return "\n".join(lines)

    def write_markdown(self, content: str, path: Path) -> None:
        path.write_text(content, encoding="utf-8")

    def _metrics_table(self, metrics: dict) -> list[str]:
        response = metrics["response"]
        efficiency = metrics["efficiency"]
        utilization = metrics["utilization"]
        fairness = metrics["fairness"]
        misassignment = metrics["misassignment"]

        lines: list[str] = []
        lines.append("")
        lines.append("| 指标类别 | 指标名称 | 数值 |")
        lines.append("| --- | --- | --- |")
        lines.append(f"| 紧急工单响应 | P1 工单平均等待时长 | {response['p1_avg_wait_minutes']:.3f} |")
        lines.append(f"| 紧急工单响应 | P1 工单 P95 等待时长 | {response['p1_p95_wait_minutes']:.3f} |")
        lines.append(f"| 紧急工单响应 | P1 工单 SLA 达成率 | {response['p1_sla_rate']:.3f} |")
        lines.append(f"| 总体处理效率 | 全部工单平均等待时长 | {efficiency['avg_wait_minutes']:.3f} |")
        lines.append(f"| 总体处理效率 | 全部工单平均完成时长 | {efficiency['avg_completion_minutes']:.3f} |")
        lines.append(f"| 总体处理效率 | 工单队列平均长度 | {efficiency['avg_queue_length']:.3f} |")
        lines.append(f"| 总体处理效率 | 工单转派率 | {efficiency['reroute_rate']:.3f} |")
        lines.append(f"| 人员利用率 | 客服平均利用率 | {utilization['avg_agent_utilization']:.3f} |")
        lines.append(f"| 人员利用率 | 客服利用率方差 | {utilization['agent_utilization_variance']:.6f} |")
        lines.append(f"| 人员利用率 | 高峰时段系统吞吐量 | {utilization['peak_hour_throughput']} |")
        lines.append(f"| 公平性 | 每位客服处理工单数最大值 | {fairness['max_tickets_per_agent']} |")
        lines.append(f"| 公平性 | 每位客服处理工单数最小值 | {fairness['min_tickets_per_agent']} |")
        lines.append(f"| 公平性 | 每位客服处理工单数方差 | {fairness['ticket_count_variance']:.6f} |")
        lines.append(f"| 公平性 | 最长未被处理普通工单等待时长 | {fairness['longest_normal_wait_minutes']:.3f} |")
        lines.append(f"| 公平性 | 饥饿工单数 | {fairness['starvation_ticket_count']} |")
        lines.append(f"| 错误分配 | 技能不匹配分配次数 | {misassignment['mismatch_assignment_count']} |")
        lines.append(f"| 错误分配 | 因转派带来的额外处理成本总时长 | {misassignment['reroute_extra_cost_minutes']} |")
        lines.append("")
        return lines

    def _summary_table(self, result: dict) -> list[str]:
        lines: list[str] = []
        lines.append("")
        lines.append("| 摘要项 | 数值 |")
        lines.append("| --- | --- |")
        lines.append(f"| 仿真结束时间 | {result['final_time']} |")
        lines.append(f"| 最终队列长度 | {result['queue_size']} |")
        lines.append(f"| 客服总数 | {len(result['agents'])} |")
        lines.append(f"| 工单总数 | {len(result['tickets'])} |")
        lines.append("")
        lines.append("| 客服 | 最终状态 | 最大并发 | 已处理工单数 |")
        lines.append("| --- | --- | --- | --- |")
        for agent in result["agents"]:
            lines.append(
                f"| {agent['agent_id']} | {agent['status']} | {agent['max_concurrent']} | {agent['handled_ticket_count']} |"
            )
        lines.append("")
        return lines

    def _log_sample_table(self, logs: list[dict]) -> list[str]:
        lines: list[str] = []
        lines.append("")
        lines.append("| 时间 | 动作 | 工单 | 详情 |")
        lines.append("| --- | --- | --- | --- |")
        for entry in logs[: min(8, len(logs))]:
            details_text = "；".join(
                f"{key}={value}" for key, value in entry["details"].items()
            ) or "-"
            ticket_id = entry["ticket_id"] or "-"
            lines.append(
                f"| {entry['time']} | {entry['action']} | {ticket_id} | {details_text} |"
            )
        lines.append("")
        return lines
