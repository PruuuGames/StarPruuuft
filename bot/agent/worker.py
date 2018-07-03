from .agent import Agent

import sc2
from sc2.constants import *


class WorkerAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

    async def on_step(self, bot, iteration):
        """
        :param sc2.BotAI bot:
        :param iteration:
        """
        cc = bot.units(UnitTypeId.COMMANDCENTER).ready
        if not cc.exists:
            return
        else:
            cc = cc.first

        for scv in bot.units(UnitTypeId.SCV).idle:
            await bot.do(scv.gather(bot.state.mineral_field.closest_to(cc)))
