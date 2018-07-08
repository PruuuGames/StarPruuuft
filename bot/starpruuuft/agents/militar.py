import sc2
from sc2.constants import *

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent
from .. import utilities

class MilitarAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self._INITIAL_AMOUNT_MARINES = 4
        self._MAX_AMOUNT_MARINES = 20
        self._MAX_AMOUNT_MARAUDERS = 6

        self.add_message_handler(AgentMessage.BARRACKS_TECHLAB_READY, self._handle_barracks_techlab_ready)
        self.add_message_handler(AgentMessage.BARRACKS_REACTOR_READY, self._handle_barracks_reactor_ready)

        self._marine_amount = 0
        self._marauder_amount = 0

        self._initial_state = True
        self._reactor_ready = False
        self._techlab_ready = False

    async def on_step(self, bot, iteration):

        self._marine_amount = bot.units(UnitTypeId.MARINE).amount
        self._marauder_amount = bot.units(UnitTypeId.MARAUDER).amount
        barracks = (bot.units(UnitTypeId.BARRACKS)).ready

        if self._initial_state and barracks.exists:
            if self._marine_amount < self._INITIAL_AMOUNT_MARINES:
                await self._train_units(bot, UnitTypeId.MARINE, self._INITIAL_AMOUNT_MARINES, barracks)
            elif self._marine_amount == self._INITIAL_AMOUNT_MARINES:
                self._initial_state = False
                self.send("BuilderAgent", AgentMessage.BUILD_BARRACKS)

        if self._techlab_ready:
            #NAO TA ENVIANDO A MENSAGEM PARA DEIXAR TECHLAB_READY = TRUE
            if self._marauder_amount < self._MAX_AMOUNT_MARAUDERS:
                await self._train_units(bot, UnitTypeId.MARAUDER, self._MAX_AMOUNT_MARAUDERS, barracks)

        if self._reactor_ready:
            if self._marine_amount < self._MAX_AMOUNT_MARAUDERS:
                await self._train_units(bot,  UnitTypeId.MARAUDER, self._MAX_AMOUNT_MARINES, barracks)


    def _handle_barracks_techlab_ready(self, *args):
        self._techlab_ready = True

    def _handle_barracks_reactor_ready(self, *args):
        self._reactor_ready = True

    async def _train_units(self, bot, unit_type, max_amount, barracks):
        for barrack in barracks:
            if bot.supply_left > 0 and bot.units(unit_type).amount < max_amount and bot.can_afford(unit_type) and barrack.noqueue:
                await bot.do(barrack.train(unit_type))