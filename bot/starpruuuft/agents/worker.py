from sc2.constants import *

from .agent import Agent
from .. import utilities


class WorkerAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

    async def on_step(self, bot, iteration):
        # Caso não exista CC, o agente não faz nada
        cc = utilities.get_command_center(bot)
        if cc is None:
            return

        await self._refinery_assign_workers(bot)
        await self._mineral_assign_workers(bot, cc)
        await self._mineral_assign_mules(bot, cc)

    # Verifica se alguma refinaria está sem a quantidade ideal de trabalhadores e redistribui, caso necessário
    async def _refinery_assign_workers(self, bot):
        for refinery in bot.get_units(UnitTypeId.REFINERY):
            if refinery.assigned_harvesters < refinery.ideal_harvesters:
                worker = bot.workers.closer_than(20, refinery)
                if worker.exists:
                    await bot.do(worker.random.gather(refinery))

    # Envia todos os SCVs em idle para minerar
    async def _mineral_assign_workers(self, bot, cc):
        for scv in bot.get_units(UnitTypeId.SCV).idle:
            await bot.do(scv.gather(bot.state.mineral_field.closest_to(cc)))

    # Envia todas as MULEs em idle para minerar
    async def _mineral_assign_mules(self, bot, cc):
        # Caso não tenha o upgrade do orbital, não podem haver MULEs
        if cc.type_id is not UnitTypeId.ORBITALCOMMAND:
            return

        for mule in bot.get_units(UnitTypeId.MULE).idle:
            await bot.do(mule(AbilityId.HARVEST_GATHER_MULE, bot.state.mineral_field.closest_to(cc)))

