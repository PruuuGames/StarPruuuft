from .agent import Agent

import sc2
from sc2.constants import *
from sc2.position import Point2


class BuilderAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self._tracked_depots = []

        self._depots_locations = None
        self.raised = False

    def _setup_depos(self, bot):
        self._depots_locations = [
            Point2((max({p.x for p in d}), min({p.y for p in d})))
            for d in bot.main_base_ramp.top_wall_depos
        ]

    async def _build_supply_depot(self, bot, cc):
        depots = (bot.units(UnitTypeId.SUPPLYDEPOT).ready | bot.units(UnitTypeId.SUPPLYDEPOTLOWERED).ready)
        depot_count = depots.amount

        not_tracked_depots = [depot for depot in depots if depot.tag not in self._tracked_depots]

        for depot in not_tracked_depots:
            self._tracked_depots.append(depot.tag)
            if self.raised and depot.type_id == UnitTypeId.SUPPLYDEPOTLOWERED:
                await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE))
            elif not self.raised and depot.type_id == UnitTypeId.SUPPLYDEPOT:
                await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

        if depot_count >= 1 and bot.supply_left > 30:
            return

        if bot.can_afford(UnitTypeId.SUPPLYDEPOT) and not bot.already_pending(UnitTypeId.SUPPLYDEPOT):
            if depot_count < len(self._depots_locations):
                depot_location = list(self._depots_locations)[depot_count]
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=depot_location, max_distance=2, placement_step=1)
            else:
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(
                        bot.game_info.map_center, 5))

    async def on_step(self, bot, iteration):
        """
        :param sc2.BotAI bot:
        :param iteration:
        """
        if self._depots_locations is None:
            self._setup_depos(bot)

        cc = bot.units(UnitTypeId.COMMANDCENTER)
        if not cc.exists:
            return
        else:
            cc = cc.first

        await self._build_supply_depot(bot, cc)
