from sc2.constants import *

from .agent import Agent
from .. import utilities, constants as pru

SUPPLY_USAGE = {
    UnitTypeId.MARINE: 1,
    UnitTypeId.MARAUDER: 2,
    UnitTypeId.SIEGETANK: 3,
    UnitTypeId.MEDIVAC: 2,
    UnitTypeId.LIBERATOR: 3,
}


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
        self._barracks_ready = 0

        self._medivac_cargo = {}

    async def on_step(self, bot, iteration):
        await self._train_marine(bot)
        await self._train_marauder(bot)
        await self._train(bot, UnitTypeId.SIEGETANK, self._factory_tech, self._siege_tank, pru.SIEGE_TANK_MAX_AMOUNT)
        await self._train(bot, UnitTypeId.MEDIVAC, self._starport_reactor, self._medivac, pru.MEDIVAC_MAX_AMOUNT)
        await self._train(bot, UnitTypeId.LIBERATOR, self._starport_reactor, self._liberator, pru.LIBERATOR_MAX_AMOUNT)

    async def _train(self, bot, unit_type, structure, current_amount, max_amount):
        if structure is None or not structure.is_ready or bot.supply_left < SUPPLY_USAGE[unit_type]:
            return

        if current_amount >= max_amount:
            return

        queue_size = 2 if (structure is self._barracks_reactor or structure is self._starport_reactor) else 1

        pending = bot.already_pending(unit_type)
        if pending < queue_size - len(structure.orders) and bot.can_afford(unit_type):
            await bot.do(structure.train(unit_type))

    async def _train_marine(self, bot):
        structure = self._barracks_clear

        if self._barracks_ready > 1 and structure is not None:
            structure = None

        if self._barracks_clear is None:
            if self._barracks_reactor is not None:
                structure = self._barracks_reactor
            else:
                structure = self._barracks_tech
                if self._marauder * 2 < self._marine:
                    return

        await self._train(bot, UnitTypeId.MARINE, structure, self._marine, pru.MARINE_MAX_AMOUNT)

        if structure is self._barracks_reactor and self._marauder >= pru.MARAUDERS_MAX_AMOUNT:
            await self._train(bot, UnitTypeId.MARINE, self._barracks_tech, self._marine, pru.MARINE_MAX_AMOUNT)

    async def _train_marauder(self, bot):
        if self._barracks_tech is None:
            return

        if self._barracks_reactor is None and self._marauder * 2 >= self._marine:
            return

        await self._train(bot, UnitTypeId.MARAUDER, self._barracks_tech, self._marauder, pru.MARAUDERS_MAX_AMOUNT)

    def _cache(self, bot):
        self._barracks_clear, self._barracks_tech, self._barracks_reactor = utilities.get_barracks(bot)
        _, self._factory_tech = utilities.get_factory(bot)
        _, self._starport_reactor = utilities.get_starport(bot)

        self._barracks_ready = len((bot.units(UnitTypeId.BARRACKS)).ready)

        self._marine = bot.get_units(UnitTypeId.MARINE).amount
        self._marauder = bot.get_units(UnitTypeId.MARAUDER).amount
        self._siege_tank = bot.get_units(UnitTypeId.SIEGETANK).amount
        self._siege_tank += bot.get_units(UnitTypeId.SIEGETANKSIEGED).amount
        self._medivac = bot.get_units(UnitTypeId.MEDIVAC).amount
        self._liberator = bot.get_units(UnitTypeId.LIBERATOR).amount
        self._liberator += bot.get_units(UnitTypeId.LIBERATORAG).amount

        self._marine += bot.get_pending_orders(AbilityId.BARRACKSTRAIN_MARINE)
        self._marauder += bot.get_pending_orders(AbilityId.BARRACKSTRAIN_MARAUDER)
        self._siege_tank += bot.get_pending_orders(AbilityId.FACTORYTRAIN_SIEGETANK)
        self._medivac += bot.get_pending_orders(AbilityId.STARPORTTRAIN_MEDIVAC)
        self._liberator += bot.get_pending_orders(AbilityId.STARPORTTRAIN_LIBERATOR)
