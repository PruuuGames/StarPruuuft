from sc2.constants import *

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent
from .. import utilities


class BaseAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

    async def on_step(self, bot, iteration):
        # Caso não exista CC, o agente não faz nada
        cc = utilities.get_command_center(bot)
        if cc is None:
            return

        await self._train_scvs(bot, cc)

    async def _train_scvs(self, bot, cc):
        # API não retorna corretamente a quantidade de workers, diferença de 2 observada
        train = bot.supply_left > 0 and bot.workers.amount < (23 - 2)

        if not train:
            return

        if cc.noqueue and bot.can_afford(UnitTypeId.SCV):
            await bot.do(cc.train(UnitTypeId.SCV))

