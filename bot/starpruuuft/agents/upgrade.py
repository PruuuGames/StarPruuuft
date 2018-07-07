from sc2.constants import *

from .agent import Agent
from .. import utilities

ORBITAL_UPGRADE_CHECK_DELAY = 20


class UpgradeAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

    async def on_step(self, bot, iteration):
        # Caso não exista CC, o agente não faz nada
        cc = utilities.get_command_center(bot)
        if cc is None:
            return

        await self._upgrade_command_center(bot, iteration, cc)

    async def _upgrade_command_center(self, bot, iteration, cc):
        if cc.type_id is UnitTypeId.ORBITALCOMMAND:
            return

        if iteration % ORBITAL_UPGRADE_CHECK_DELAY != 0:
            return

        # Se já estiver fazendo o upgrade, corta a execução
        # todo

        barracks = bot.units.filter(lambda unit: unit.is_ready and unit.type_id is UnitTypeId.BARRACKS)
        if barracks.amount == 0:
            return

        # Hard coded value, since can_afford says that the upgrade needs 500 minerals
        if cc.noqueue and bot.can_afford(UnitTypeId.ORBITALCOMMAND):
            await bot.do(cc.train(UnitTypeId.ORBITALCOMMAND))
