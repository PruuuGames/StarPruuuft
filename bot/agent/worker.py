import sc2
from sc2.constants import *

from bot.agent_message import AgentMessage
from .agent import Agent


class WorkerAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self._upgrade_command_center_done = False

    def _process_messages(self):
        if len(self._messages) == 0:
            return

        for message in self._messages:
            message_type = message[0]

            if message_type is AgentMessage.UPGRADE_COMMAND_CENTER_DONE:
                self._upgrade_command_center_done = True

        self._messages = []

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

        for refinery in bot.units(UnitTypeId.REFINERY).ready:
            if refinery.assigned_harvesters < refinery.ideal_harvesters:
                worker = bot.workers.closer_than(20, refinery)
                if worker.exists:
                    await bot.do(worker.random.gather(refinery))

        for scv in bot.units(UnitTypeId.SCV).idle:
            await bot.do(scv.gather(bot.state.mineral_field.closest_to(cc)))

        if self._upgrade_command_center_done:
            for mule in bot.units(UnitTypeId.MULE).idle:
                await bot.do(mule(AbilityId.HARVEST_GATHER_MULE, bot.state.mineral_field.closest_to(cc)))
