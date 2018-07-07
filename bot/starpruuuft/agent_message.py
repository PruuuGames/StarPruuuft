from enum import Enum, auto


class AgentMessage(Enum):
    RAMP_SUPPLY_DEPOT = auto
    SUPPLY_DEPOTS_RAISED = auto
    UPGRADE_COMMAND_CENTER_READY = auto

