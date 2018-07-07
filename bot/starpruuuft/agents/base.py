from sc2.constants import *

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent
from .. import utilities


class BaseAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self.add_message_handler(AgentMessage.UPGRADE_COMMAND_CENTER_READY, self._handle_upgrade_ready)

        self._upgrade_command_center_ready = False

    def _handle_upgrade_ready(self):
        self._upgrade_command_center_ready = True

    async def on_step(self, bot, iteration):
        cc = utilities.get_command_center(bot)

        await self._train_scvs(bot, cc)
        await self._calldown_mule(bot, cc)

    async def _train_scvs(self, bot, cc):
        halt = self._upgrade_command_center_ready and cc is not UnitTypeId.ORBITALCOMMAND
        train = bot.supply_left > 0 and bot.workers.amount < 21 # Quantidade bugada, assumir 23

        if halt or not train:
            return

        if cc.noqueue and bot.can_afford(UnitTypeId.SCV):
            await bot.do(cc.train(UnitTypeId.SCV))

    async def _calldown_mule(self, bot, cc):
        calldown = cc.type_id is UnitTypeId.ORBITALCOMMAND and cc.energy >= 50

        if not calldown:
            return

        target = bot.state.mineral_field.closest_to(cc).position.to2
        await bot.do(cc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, target))

