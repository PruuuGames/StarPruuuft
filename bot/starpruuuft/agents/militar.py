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
        self._MAX_AMOUNT_SIEGE_TANK = 4
        self._MAX_AMOUNT_MEDIVAC = 2
        self._MAX_AMOUNT_LIBERATOR = 1

        #Falta consertar essas comunicações para trabalhar com as variáveis para mostrar a comunicação entre agentes
        self.add_message_handler(AgentMessage.BARRACKS_TECHLAB_READY, self._handle_barracks_techlab_ready)
        self.add_message_handler(AgentMessage.BARRACKS_REACTOR_READY, self._handle_barracks_reactor_ready)
        #Falta adiocinar os outros message handler para as outras construções (factory, starpot)

        self._marine_amount = 0
        self._marauder_amount = 0
        self._siege_tank_amount = 0
        self._medivac_amount = 0
        self._liberator_amount = 0

        self._initial_state = True
        self._reactor_ready = False
        self._techlab_ready = False

    async def on_step(self, bot, iteration):

        #mudar isso de lugar para nao ficar sempre recalculando isso
        self._marine_amount = bot.units(UnitTypeId.MARINE).amount
        self._marauder_amount = bot.units(UnitTypeId.MARAUDER).amount
        self._siege_tank_amount = bot.units(UnitTypeId.SIEGETANK).amount
        self._medivac_amount = bot.units(UnitTypeId.MEDIVAC).amount
        self._liberator_amount = bot.units(UnitTypeId.LIBERATOR).amount

        barracks = (bot.units(UnitTypeId.BARRACKS)).ready
        #Estado inicial
        if self._initial_state and barracks.exists:
            if self._marine_amount < self._INITIAL_AMOUNT_MARINES:
                await self._train_units(bot, UnitTypeId.MARINE, self._INITIAL_AMOUNT_MARINES, barracks)
            elif self._marine_amount == self._INITIAL_AMOUNT_MARINES:
                self._initial_state = False
                self.send("BuilderAgent", AgentMessage.BUILD_BARRACKS)

        #Barracks TechLab
        # NAO TA ENVIANDO A MENSAGEM PARA DEIXAR TECHLAB_READY = TRUE
        #if self._techlab_ready:
        if (bot.units(UnitTypeId.BARRACKSTECHLAB)).ready.exists:

            if self._marauder_amount < self._MAX_AMOUNT_MARAUDERS:
                await self._train_units(bot, UnitTypeId.MARAUDER, self._MAX_AMOUNT_MARAUDERS, barracks)
            elif self._marine_amount < self._MAX_AMOUNT_MARINES:
                await self._train_units(bot, UnitTypeId.MARINE, self._MAX_AMOUNT_MARINES, barracks)

        #Barracks Reactor
        #if self._reactor_ready:
        if (bot.units(UnitTypeId.BARRACKSREACTOR)).ready.exists:
            if self._marine_amount < self._MAX_AMOUNT_MARINES:
                await self._train_units(bot, UnitTypeId.MARINE, self._MAX_AMOUNT_MARINES, barracks)

        #Factory
        if (bot.units(UnitTypeId.FACTORYTECHLAB)).ready.exists:
            factory = (bot.units(UnitTypeId.FACTORY)).ready
            if self._siege_tank_amount < self._MAX_AMOUNT_SIEGE_TANK:
                await self._train_units(bot, UnitTypeId.SIEGETANK, self._MAX_AMOUNT_SIEGE_TANK, factory)

        #Starport
        if (bot.units(UnitTypeId.STARPORT)).ready.exists:
            starport = (bot.units(UnitTypeId.STARPORT)).ready
            if self._medivac_amount < self._MAX_AMOUNT_MEDIVAC:
                await self._train_units(bot, UnitTypeId.MEDIVAC, self._MAX_AMOUNT_MEDIVAC, starport)
            if self._liberator_amount < self._MAX_AMOUNT_LIBERATOR:
                await self._train_units(bot, UnitTypeId.LIBERATOR, self._MAX_AMOUNT_LIBERATOR, starport)


    def _handle_barracks_techlab_ready(self, *args):
        self._techlab_ready = True

    def _handle_barracks_reactor_ready(self, *args): #mensagem dele esta chegando aqui
        self._reactor_ready = True

    async def _train_units(self, bot, unit_type, max_amount, units):
        for unit in units:
            if bot.supply_left > 0 and bot.units(unit_type).amount < max_amount and bot.can_afford(unit_type) and unit.noqueue:
                await bot.do(unit.train(unit_type))