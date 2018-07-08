from enum import Enum, auto


class AgentMessage(Enum):
    RAMP_SUPPLY_DEPOT = auto
    ENEMIES_CLOSE = auto
    BARRACKS_READY = auto
    BUILD_BARRACKS = auto
    BARRACKS_REACTOR_READY = auto
    BARRACKS_TECHLAB_READY = auto

