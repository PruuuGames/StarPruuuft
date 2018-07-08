from sc2.constants import *

from .agent import Agent
from .. import utilities, constants as pru


class MilitarAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self._barracks_clear = None
        self._barracks_tech = None
        self._barracks_reactor = None
        self._factory_tech = None
        self._starport_reactor = None

        self._marine = 0
        self._marauder = 0
        self._siege_tank = 0
        self._medivac = 0
        self._liberator = 0

        self._medivac_load = {}
        self._medivac_loaded = set()

    async def on_step(self, bot, iteration):
        await self._train_marine(bot)
        await self._train_marauder(bot)
        await self._train(bot, UnitTypeId.SIEGETANK, self._factory_tech, self._siege_tank, pru.SIEGE_TANK_MAX_AMOUNT)
        await self._train(bot, UnitTypeId.MEDIVAC, self._starport_reactor, self._medivac, pru.MEDIVAC_MAX_AMOUNT)
        await self._train(bot, UnitTypeId.LIBERATOR, self._starport_reactor, self._liberator, pru.LIBERATOR_MAX_AMOUNT)
        await self._load_medivac(bot)

    async def _train(self, bot, unit_type, structure, current_amount, max_amount):
        if structure is None or not structure.is_ready or bot.supply_left == 0:
            return

        if current_amount >= max_amount or not structure.noqueue:
            return

        if bot.can_afford(unit_type):
            await bot.do(structure.train(unit_type))

    async def _train_marine(self, bot):
        structure = self._barracks_clear

        if self._barracks_clear is None:
            if self._barracks_reactor is not None:
                structure = self._barracks_reactor
            else:
                structure = self._barracks_tech
                if self._marauder * 2 < self._marine:
                    return

        await self._train(bot, UnitTypeId.MARINE, structure, self._marine, pru.MARINE_MAX_AMOUNT)

    async def _train_marauder(self, bot):
        if self._barracks_tech is None:
            return

        if self._barracks_reactor is None and self._marauder * 2 >= self._marine:
            return

        await self._train(bot, UnitTypeId.MARAUDER, self._barracks_tech, self._marauder, pru.MARAUDERS_MAX_AMOUNT)

    async def _load_medivac(self, bot):
        for medivac in bot.units(UnitTypeId.MEDIVAC).idle:
            load = self._medivac_load.setdefault(medivac.tag, {
                UnitTypeId.MARINE: 2,
                UnitTypeId.MARAUDER: 1,
                UnitTypeId.SIEGETANK: 1})
            for unitType in load.keys():
                for unit in bot.units(unitType).idle:
                    if load[unitType] and unit.tag not in self._medivac_loaded:
                        await bot.do(medivac(AbilityId.LOAD_MEDIVAC, unit))
                        self._medivac_loaded.add(unit.tag)
                        load[unitType] -= 1
                        return

    def _cache(self, bot):
        self._barracks_clear, self._barracks_tech, self._barracks_reactor = utilities.get_barracks(bot)
        _, self._factory_tech = utilities.get_factory(bot)
        _, self._starport_reactor = utilities.get_starport(bot)

        self._marine = bot.get_units(UnitTypeId.MARINE).amount
        self._marauder = bot.get_units(UnitTypeId.MARAUDER).amount
        self._siege_tank = bot.get_units(UnitTypeId.SIEGETANK).amount
        self._siege_tank += bot.get_units(UnitTypeId.SIEGETANKSIEGED).amount
        self._medivac = bot.get_units(UnitTypeId.MEDIVAC).amount
        self._liberator = bot.get_units(UnitTypeId.LIBERATOR).amount
        self._liberator += bot.get_units(UnitTypeId.LIBERATORAG).amount

        self._marine += bot.get_units(UnitTypeId.MARINE, ready=False).amount
        self._marauder += bot.get_units(UnitTypeId.MARAUDER, ready=False).amount
        self._siege_tank += bot.get_units(UnitTypeId.SIEGETANK, ready=False).amount
        self._siege_tank += bot.get_units(UnitTypeId.SIEGETANKSIEGED, ready=False).amount
        self._medivac += bot.get_units(UnitTypeId.MEDIVAC, ready=False).amount
        self._liberator += bot.get_units(UnitTypeId.LIBERATOR, ready=False).amount
        self._liberator += bot.get_units(UnitTypeId.LIBERATORAG, ready=False).amount
