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

        for refinery in bot.units(UnitTypeId.REFINERY).ready:
            if refinery.assigned_harvesters < refinery.ideal_harvesters:
                worker = bot.workers.closer_than(20, refinery)
                if worker.exists:
                    await bot.do(worker.random.gather(refinery))

        for scv in bot.units(UnitTypeId.SCV).idle:
            await bot.do(scv.gather(bot.state.mineral_field.closest_to(cc)))
