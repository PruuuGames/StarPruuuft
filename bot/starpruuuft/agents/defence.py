from sc2.constants import *

from .agent import Agent
from .. import utilities, constants as pru


class DefenceAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)
        pass

        # self._barracks_clear = None
        # self._barracks_tech = None
        # self._barracks_reactor = None
        # self._factory_tech = None
        # self._starport_reactor = None

        # self._marine = 0
        # self._marauder = 0
        # self._siege_tank = 0
        # self._medivac = 0
        # self._liberator = 0

        # self._medivac_cargo = {}

    async def on_step(self, bot, iteration):
        pass
        # await self._train_marine(bot)
        # await self._train_marauder(bot)
        # await self._train(bot, UnitTypeId.SIEGETANK, self._factory_tech, self._siege_tank, pru.SIEGE_TANK_MAX_AMOUNT)
        # await self._train(bot, UnitTypeId.MEDIVAC, self._starport_reactor, self._medivac, pru.MEDIVAC_MAX_AMOUNT)
        # await self._train(bot, UnitTypeId.LIBERATOR, self._starport_reactor, self._liberator, pru.LIBERATOR_MAX_AMOUNT)
        # await self._load_medivac(bot)

    def _cache(self, bot):
        pass
        # self._barracks_clear, self._barracks_tech, self._barracks_reactor = utilities.get_barracks(bot)
        # _, self._factory_tech = utilities.get_factory(bot)
        # _, self._starport_reactor = utilities.get_starport(bot)

        # self._marine = bot.get_units(UnitTypeId.MARINE).amount
        # self._marauder = bot.get_units(UnitTypeId.MARAUDER).amount
        # self._siege_tank = bot.get_units(UnitTypeId.SIEGETANK).amount
        # self._siege_tank += bot.get_units(UnitTypeId.SIEGETANKSIEGED).amount
        # self._medivac = bot.get_units(UnitTypeId.MEDIVAC).amount
        # self._liberator = bot.get_units(UnitTypeId.LIBERATOR).amount
        # self._liberator += bot.get_units(UnitTypeId.LIBERATORAG).amount

        # self._marine += bot.get_units(UnitTypeId.MARINE, ready=False).amount
        # self._marauder += bot.get_units(UnitTypeId.MARAUDER, ready=False).amount
        # self._siege_tank += bot.get_units(UnitTypeId.SIEGETANK, ready=False).amount
        # self._siege_tank += bot.get_units(UnitTypeId.SIEGETANKSIEGED, ready=False).amount
        # self._medivac += bot.get_units(UnitTypeId.MEDIVAC, ready=False).amount
        # self._liberator += bot.get_units(UnitTypeId.LIBERATOR, ready=False).amount
        # self._liberator += bot.get_units(UnitTypeId.LIBERATORAG, ready=False).amount
