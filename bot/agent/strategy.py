from .agent import Agent

import sc2
from sc2.constants import *

SUPPLY_DEPOT_DANGER_DISTANCE = 11


class StrategyAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self.supplies_raised = False

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

        # Get only ramp depots from builder agent
        lowered_depots = bot.units(UnitTypeId.SUPPLYDEPOTLOWERED).ready
        raised_depots = bot.units(UnitTypeId.SUPPLYDEPOT).ready
        enemies_near = self._enemies_near(bot, lowered_depots | raised_depots)
        morphing = []

        if self.supplies_raised != enemies_near:
            if self.supplies_raised:
                morphing = [depot for depot in raised_depots]
            else:
                morphing = [depot for depot in lowered_depots]

            self.supplies_raised = enemies_near
            # broadcast information to BuilderAgent

        if self.supplies_raised:
            [await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)) for depot in morphing]
        else:
            [await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)) for depot in morphing]

    async def on_step(self, bot, iteration):
        """
        :param sc2.BotAI bot:
        :param iteration:
        """

        await self._handle_supply_depots(bot, iteration)
