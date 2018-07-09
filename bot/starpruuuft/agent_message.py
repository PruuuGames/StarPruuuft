from enum import Enum


class AgentMessage(Enum):
    RAMP_SUPPLY_DEPOT = 1
    ENEMIES_CLOSE = 2
    BARRACKS_READY = 3
    ATTACKING = 4

