from sc2.constants import *

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent
from .. import utilities

SUPPLY_DEPOT_DANGER_DISTANCE = 11
SUPPLY_DEPOT_CHECK_DELAY = 20


class StrategyAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self.add_message_handler(AgentMessage.RAMP_SUPPLY_DEPOT, self._handle_ramp_supply_depot)

        self._supplies_raised = False
        self._ramp_supply_depots = []

    async def on_step(self, bot, iteration):
        await self._handle_supply_depots(bot, iteration)

    # Reconhece um depot localizado na rampa
    def _handle_ramp_supply_depot(self, *args):
        self._ramp_supply_depots.append(args[0])

    async def _handle_supply_depots(self, bot, iteration):
        if iteration % SUPPLY_DEPOT_CHECK_DELAY != 0:
            return

        # Lida com os depots da rampa
        ramp_depots = bot.units.filter(lambda unit: unit.tag in self._ramp_supply_depots)
        lowered_depots = ramp_depots.filter(lambda unit: unit.type_id is UnitTypeId.SUPPLYDEPOTLOWERED)
        raised_depots = ramp_depots.filter(lambda unit: unit.type_id is UnitTypeId.SUPPLYDEPOT)
        enemies_near = utilities.any_enemies_near(bot, lowered_depots | raised_depots, SUPPLY_DEPOT_DANGER_DISTANCE)
        morphing = []

        # Caso o estado dos depots deva mudar
        if self._supplies_raised != enemies_near:
            if self._supplies_raised:
                morphing = [depot for depot in raised_depots]
            else:
                morphing = [depot for depot in lowered_depots]

            # Atualiza o estado e faz broadcast da informação
            self._supplies_raised = enemies_near
            self.broadcast(AgentMessage.ENEMIES_CLOSE, enemies_near)

        # Ajusta os depots
        if self._supplies_raised:
            [await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)) for depot in morphing]
        else:
            [await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)) for depot in morphing]
