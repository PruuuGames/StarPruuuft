import sc2
from sc2.constants import *

from bot.agent_message import AgentMessage
from .agent import Agent

SUPPLY_DEPOT_DANGER_DISTANCE = 11


class StrategyAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self.supplies_raised = False
        self._ramp_supply_depots = []

    def _process_messages(self):
        if len(self._messages) == 0:
            return

        for message in self._messages:
            message_type = message[0]

            if message_type is AgentMessage.RAMP_SUPPLY_DEPOT:
                self._ramp_supply_depots.append(message[1][0])

        self._messages = []

    @staticmethod
    def _enemies_near(bot, units):
        enemy_units = bot.known_enemy_units.not_structure

        for enemy in enemy_units:
            for unit in units:
                if unit.position.to2.distance_to(enemy.position.to2) <= SUPPLY_DEPOT_DANGER_DISTANCE:
                    return True

        return False

    async def _handle_supply_depots(self, bot, iteration):
        if not iteration % 10 == 0:
            return

        ramp_depots = bot.units.filter(lambda unit: unit.tag in self._ramp_supply_depots)
        lowered_depots = ramp_depots.filter(lambda unit: unit.type_id is UnitTypeId.SUPPLYDEPOTLOWERED)
        raised_depots = ramp_depots.filter(lambda unit: unit.type_id is UnitTypeId.SUPPLYDEPOT)
        enemies_near = self._enemies_near(bot, lowered_depots | raised_depots)
        morphing = []

        if self.supplies_raised != enemies_near:
            if self.supplies_raised:
                morphing = [depot for depot in raised_depots]
            else:
                morphing = [depot for depot in lowered_depots]

            self.supplies_raised = enemies_near
            self.send("BuilderAgent", AgentMessage.SUPPLY_DEPOTS_RAISED, enemies_near)

        if self.supplies_raised:
            [await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)) for depot in morphing]
        else:
            [await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)) for depot in morphing]

    async def on_step(self, bot, iteration):
        """
        :param sc2.BotAI bot:
        :param iteration:
        """

        self._process_messages()

        await self._handle_supply_depots(bot, iteration)
