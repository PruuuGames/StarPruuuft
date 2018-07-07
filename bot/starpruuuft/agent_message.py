from enum import Enum, auto


class AgentMessage(Enum):
    RAMP_SUPPLY_DEPOT = auto
    ENEMIES_CLOSE = auto
    BARRACKS_READY = auto

