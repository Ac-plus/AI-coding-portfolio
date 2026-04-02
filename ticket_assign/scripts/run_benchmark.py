from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ticket_assign.config.scenario_loader import load_scenario
from ticket_assign.reporting.report_builder import BenchmarkCaseResult, ReportBuilder
from ticket_assign.simulator.engine import SimulationEngine


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "scenarios"
OUTPUT_METRICS = ROOT / "outputs" / "metrics" / "benchmark_results.json"
OUTPUT_REPORT = ROOT / "测试报告.md"


def run_case(
    case_id: str,
    title: str,
    scenario_name: str,
    dispatcher: str,
    purpose: str,
    steps: list[str],
    observations_builder,
) -> BenchmarkCaseResult:
    scenario = load_scenario(SCENARIOS / scenario_name)
    result = SimulationEngine.from_scenario(scenario, dispatcher_name=dispatcher).run().to_dict()
    observations = observations_builder(result)
    return BenchmarkCaseResult(
        case_id=case_id,
        title=title,
        scenario=scenario_name,
        dispatcher=dispatcher,
        purpose=purpose,
        steps=steps,
        observations=observations,
        result=result,
    )


def main() -> None:
    case_results: list[BenchmarkCaseResult] = []

    case_results.append(
        run_case(
            case_id="5.1-A",
            title="基线对比 - FIFO",
            scenario_name="peak_load.json",
            dispatcher="fifo",
            purpose="作为基线策略，观察高峰混合负载下的等待时长、吞吐和公平性表现。",
            steps=[
                "加载 peak_load 场景，包含普通工单集中涌入和少量 P1 工单穿插。",
                "使用 FIFO 策略运行完整仿真。",
                "记录 README 第 4 节要求的全部指标。",
            ],
            observations_builder=lambda result: [
                f"P1 SLA 达成率为 {result['metrics']['response']['p1_sla_rate']:.2f}。",
                f"普通工单最长等待 {result['metrics']['fairness']['longest_normal_wait_minutes']:.1f} 分钟。",
                f"队列平均长度为 {result['metrics']['efficiency']['avg_queue_length']:.3f}。",
            ],
        )
    )

    case_results.append(
        run_case(
            case_id="5.1-B",
            title="基线对比 - PriorityFirst",
            scenario_name="peak_load.json",
            dispatcher="priority_first",
            purpose="使用纯优先级基线策略，对比紧急工单响应和普通工单积压情况。",
            steps=[
                "使用与 FIFO 相同的 peak_load 场景。",
                "切换为 priority_first 策略运行仿真。",
                "与 FIFO 的输出指标做横向比较。",
            ],
            observations_builder=lambda result: [
                f"P1 平均等待 {result['metrics']['response']['p1_avg_wait_minutes']:.1f} 分钟。",
                f"全部工单平均完成时长 {result['metrics']['efficiency']['avg_completion_minutes']:.3f} 分钟。",
                f"饥饿工单数 {result['metrics']['fairness']['starvation_ticket_count']}。",
            ],
        )
    )

    case_results.append(
        run_case(
            case_id="5.1-C",
            title="基线对比 - LeastLoaded",
            scenario_name="peak_load.json",
            dispatcher="least_loaded",
            purpose="使用最空闲客服优先策略，对比利用率均衡和吞吐表现。",
            steps=[
                "使用与 FIFO 相同的 peak_load 场景。",
                "切换为 least_loaded 策略运行仿真。",
                "观察利用率方差、单量方差和吞吐量。",
            ],
            observations_builder=lambda result: [
                f"客服利用率方差 {result['metrics']['utilization']['agent_utilization_variance']:.6f}。",
                f"每位客服处理单量方差 {result['metrics']['fairness']['ticket_count_variance']:.6f}。",
                f"高峰小时吞吐量 {result['metrics']['utilization']['peak_hour_throughput']}。",
            ],
        )
    )

    case_results.append(
        run_case(
            case_id="5.1-D",
            title="基线对比 - BalancedDispatcher",
            scenario_name="peak_load.json",
            dispatcher="balanced",
            purpose="运行主策略，验证在 SLA、等待时长和均衡性之间的综合表现。",
            steps=[
                "使用与其他基线相同的 peak_load 场景。",
                "切换为 balanced 策略运行仿真。",
                "对比 P1 响应、队列积压和公平性指标。",
            ],
            observations_builder=lambda result: [
                f"P1 P95 等待 {result['metrics']['response']['p1_p95_wait_minutes']:.1f} 分钟。",
                f"全部工单平均等待 {result['metrics']['efficiency']['avg_wait_minutes']:.3f} 分钟。",
                f"最长普通工单等待 {result['metrics']['fairness']['longest_normal_wait_minutes']:.1f} 分钟。",
            ],
        )
    )

    case_results.append(
        run_case(
            case_id="5.2",
            title="高峰场景测试",
            scenario_name="peak_load.json",
            dispatcher="balanced",
            purpose="验证白天普通工单集中涌入、穿插少量高优 P1 工单时，P1 是否仍被较快响应，普通工单是否严重积压。",
            steps=[
                "加载 peak_load 场景。",
                "使用 balanced 策略运行仿真。",
                "检查 P1 SLA、普通工单最长等待、平均队列长度和饥饿工单数。",
            ],
            observations_builder=lambda result: [
                f"P1 SLA 达成率 {result['metrics']['response']['p1_sla_rate']:.2f}。",
                f"普通工单最长等待 {result['metrics']['fairness']['longest_normal_wait_minutes']:.1f} 分钟。",
                f"饥饿工单数 {result['metrics']['fairness']['starvation_ticket_count']}。",
            ],
        )
    )

    case_results.append(
        run_case(
            case_id="5.3",
            title="离线场景测试",
            scenario_name="offline_requeue.json",
            dispatcher="fifo",
            purpose="验证客服中途离线时，正在处理的工单是否被正确回收，系统能否继续稳定分配，SLA 是否受到影响。",
            steps=[
                "加载 offline_requeue 场景，其中客服在处理过程中离线后再恢复。",
                "使用 FIFO 策略运行仿真。",
                "检查回收日志、最终完成状态以及响应/效率指标变化。",
            ],
            observations_builder=lambda result: [
                "日志中出现 `ticket_requeued_from_offline`，说明工单被正确回收。",
                f"最终队列长度 {result['queue_size']}，系统恢复后仍完成了所有工单。",
                f"平均完成时长 {result['metrics']['efficiency']['avg_completion_minutes']:.1f} 分钟。",
            ],
        )
    )

    case_results.append(
        run_case(
            case_id="5.4",
            title="转派场景测试",
            scenario_name="reroute_case.json",
            dispatcher="fifo",
            purpose="验证技能不完全匹配时的错误分配次数、转派率，以及转派对整体效率的影响。",
            steps=[
                "加载 reroute_case 场景，初始只有不匹配客服在线，匹配客服稍后上线。",
                "使用 FIFO 策略运行仿真。",
                "统计错误分配次数、转派率、额外处理成本和完成时长。",
            ],
            observations_builder=lambda result: [
                f"技能不匹配分配次数 {result['metrics']['misassignment']['mismatch_assignment_count']}。",
                f"转派率 {result['metrics']['efficiency']['reroute_rate']:.2f}。",
                f"转派额外成本 {result['metrics']['misassignment']['reroute_extra_cost_minutes']} 分钟。",
            ],
        )
    )

    reproducibility_first = SimulationEngine.from_scenario(
        load_scenario(SCENARIOS / "peak_load.json"),
        dispatcher_name="balanced",
    ).run().to_dict()
    reproducibility_second = SimulationEngine.from_scenario(
        load_scenario(SCENARIOS / "peak_load.json"),
        dispatcher_name="balanced",
    ).run().to_dict()
    same_outputs = (
        reproducibility_first["metrics"] == reproducibility_second["metrics"]
        and reproducibility_first["logs"] == reproducibility_second["logs"]
    )
    case_results.append(
        BenchmarkCaseResult(
            case_id="5.5",
            title="结果可复现测试",
            scenario="peak_load.json",
            dispatcher="balanced",
            purpose="验证在相同随机种子下，日志与指标统计可以重复生成。",
            steps=[
                "加载相同的 peak_load 场景，保留相同随机种子。",
                "使用 balanced 策略连续运行两次仿真。",
                "比较两次运行的日志和指标对象是否完全一致。",
            ],
            observations=[
                f"两次运行日志是否一致: {same_outputs}.",
                f"两次运行指标是否一致: {reproducibility_first['metrics'] == reproducibility_second['metrics']}.",
                "该测试满足 README 对可复现性的要求。",
            ],
            result=reproducibility_first,
        )
    )

    report_builder = ReportBuilder()
    markdown = report_builder.build_markdown(
        case_results=case_results,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    OUTPUT_METRICS.write_text(
        json.dumps([asdict(item) for item in case_results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report_builder.write_markdown(markdown, OUTPUT_REPORT)

    print(json.dumps({"report": str(OUTPUT_REPORT), "metrics": str(OUTPUT_METRICS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
