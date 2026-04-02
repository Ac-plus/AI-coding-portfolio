"""分配策略。"""

from ticket_assign.config.settings import SimulationSettings
from ticket_assign.dispatcher.balanced_dispatcher import BalancedDispatcher
from ticket_assign.dispatcher.base import Dispatcher
from ticket_assign.dispatcher.fifo import FIFODispatcher
from ticket_assign.dispatcher.least_loaded import LeastLoadedDispatcher
from ticket_assign.dispatcher.priority_first import PriorityFirstDispatcher


def build_dispatcher(name: str, settings: SimulationSettings) -> Dispatcher:
    dispatcher_map = {
        "fifo": FIFODispatcher,
        "priority_first": PriorityFirstDispatcher,
        "least_loaded": LeastLoadedDispatcher,
        "balanced": BalancedDispatcher,
    }
    try:
        return dispatcher_map[name](settings)
    except KeyError as exc:
        supported = ", ".join(sorted(dispatcher_map))
        raise ValueError(f"unsupported dispatcher '{name}', choose from: {supported}") from exc
