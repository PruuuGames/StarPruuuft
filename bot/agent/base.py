from .agent import Agent

import sc2
from sc2.constants import *


class BaseAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

    async def on_step(self, bot, iteration):
        """
        :param sc2.BotAI bot:
        :param iteration:
        """

        cc = bot.units(UnitTypeId.COMMANDCENTER)
        if not cc.exists:
            return
        else:
            cc = cc.first

        # Quantidade bugada, não reconhece bem quantos trabalhadores tem quando tem SCV nas refinarias
        if bot.supply_left > 0 and bot.workers.amount < 21 and cc.noqueue and bot.can_afford(
                UnitTypeId.SCV):
            await bot.do(cc.train(UnitTypeId.SCV))
