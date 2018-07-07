import sc2
from sc2.constants import *

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent


class UpgradeAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self._upgrade_command_center_ready = False
        self._upgrade_command_center_done = False

    def _process_messages(self):
        if len(self._messages) == 0:
            return

        for message in self._messages:
            message_type = message[0]

            if message_type is AgentMessage.UPGRADE_COMMAND_CENTER_READY:
                self._upgrade_command_center_ready = True

        self._messages = []

    async def _upgrade_command_center(self, bot, cc):
        if not self._upgrade_command_center_ready or self._upgrade_command_center_done:
            return

        # Hard coded value, since can_afford says that the upgrade needs 500 minerals
        if cc.noqueue and bot.can_afford(UnitTypeId.ORBITALCOMMAND):
            await bot.do(cc.train(UnitTypeId.ORBITALCOMMAND))

            self._upgrade_command_center_done = True
            self.send(["WorkerAgent", "BaseAgent"], AgentMessage.UPGRADE_COMMAND_CENTER_DONE)

    async def on_step(self, bot, iteration):
        """
        :param sc2.BotAI bot:
        :param iteration:
        """

        self._process_messages()

        cc = (bot.units(UnitTypeId.COMMANDCENTER) | bot.units(UnitTypeId.ORBITALCOMMAND)).ready
        if not cc.exists:
            return
        else:
            cc = cc.first

        # Quantidade bugada, não reconhece bem quantos trabalhadores tem quando tem SCV nas refinarias
        if bot.supply_left > 0 and bot.workers.amount < 21 and cc.noqueue and bot.can_afford(
                UnitTypeId.SCV):
            await bot.do(cc.train(UnitTypeId.SCV))

        await self._upgrade_command_center(bot, cc)
