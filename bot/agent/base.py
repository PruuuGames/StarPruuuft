from .agent import Agent

import sc2
from sc2.constants import *
from sc2.position import Point2


class BaseAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self._depos = None

    def _setup_depos(self, bot):
        self._depos = [
            Point2((max({p.x for p in d}), min({p.y for p in d})))
            for d in bot.main_base_ramp.top_wall_depos
        ]

    async def _try_build_depo(self, bot, depo_count, cc):
        if bot.can_afford(UnitTypeId.SUPPLYDEPOT) and not bot.already_pending(UnitTypeId.SUPPLYDEPOT):
            if depo_count < len(self._depos):
                depo = list(self._depos)[depo_count]
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=depo, max_distance=2, placement_step=1)
            else:
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(
                        bot.game_info.map_center, 5))

    async def on_step(self, bot, iteration):
        """
        :param sc2.BotAI bot:
        :param iteration:
        """
        if self._depos is None:
            self._setup_depos(bot)

        cc = bot.units(UnitTypeId.COMMANDCENTER)
        if not cc.exists:
            return
        else:
            cc = cc.first

        for depo in bot.units(UnitTypeId.SUPPLYDEPOT).ready:
            await bot.do(depo(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

        depo_count = (bot.units(UnitTypeId.SUPPLYDEPOT) | bot.units(UnitTypeId.SUPPLYDEPOTLOWERED)).amount
        if depo_count < 1 or bot.supply_left < 3:
            await self._try_build_depo(bot, depo_count, cc)

        if bot.supply_left > 0 and bot.workers.amount < 48 and cc.noqueue and bot.can_afford(UnitTypeId.SCV):
            await bot.do(cc.train(UnitTypeId.SCV))

        for scv in bot.units(UnitTypeId.SCV).idle:
            await bot.do(scv.gather(bot.state.mineral_field.closest_to(cc)))

        if iteration != 0 and iteration % 100 == 0:
            await bot.chat_send("Alow " + str(iteration))
