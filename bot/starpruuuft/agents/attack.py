from sc2.constants import *

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent
from .. import constants as pru

ATTACK_UNITS = [
    UnitTypeId.MARINE,
    UnitTypeId.MARAUDER,
    UnitTypeId.SIEGETANK,
    UnitTypeId.MEDIVAC,
    UnitTypeId.LIBERATOR,
]


class AttackAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self._marine = 0
        self._marauder = 0
        self._siege_tank = 0
        self._medivac = 0
        self._liberator = 0
        self._barracks_ready = 0

        self._medivac_cargo = {}
        self._mounted = {}
        self._mounted_counter = 0

        self._attack_is_ready = False
        self._attacking = False
        self._units_loaded = False

    async def on_step(self, bot, iteration):
        if not self._attack_is_ready and not self._attacking:
            return

        if not self._attacking:
            self._attacking = True
            self.broadcast(AgentMessage.ATTACKING, True)
            return

        if self._mounted_counter < 8:
            await self._unsiege_sieges(bot)
            await self._load_medivac(bot)
        else:
            target = bot.known_enemy_structures.random_or(bot.enemy_start_locations[0]).position

            for medivac in bot.get_units(UnitTypeId.MEDIVAC):
                if medivac.tag in self._medivac_cargo:
                    medivac_pos = medivac.position.to2
                    if target.distance_to(medivac_pos) <= 10:
                        await bot.do(medivac(AbilityId.UNLOADALLAT, medivac.position))
                        del self._medivac_cargo[medivac.tag]

            for unit in bot.get_units(ATTACK_UNITS).idle:
                await bot.do(unit.attack(target))
                return

    async def _unsiege_sieges(self, bot):
        for sieged in bot.get_units(UnitTypeId.SIEGETANKSIEGED):
            await bot.do(sieged(AbilityId.UNSIEGE_UNSIEGE))
            return

    async def _load_medivac(self, bot):
        for medivac in bot.get_units(UnitTypeId.MEDIVAC).idle:
            cargo = self._medivac_cargo.setdefault(medivac.tag, {
                UnitTypeId.MARINE: 2,
                UnitTypeId.MARAUDER: 1,
                UnitTypeId.SIEGETANK: 1})
            for unit_type in cargo.keys():
                for unit in bot.get_units(unit_type).idle:
                    if cargo[unit_type]:
                        await bot.do(medivac(AbilityId.LOAD_MEDIVAC, unit))
                        self._mounted.setdefault(unit_type, 0)
                        self._mounted[unit_type] += 1
                        self._mounted_counter += 1
                        cargo[unit_type] -= 1
                        return

    def _cache(self, bot):
        self._marine = bot.get_units(UnitTypeId.MARINE).amount
        self._marauder = bot.get_units(UnitTypeId.MARAUDER).amount
        self._siege_tank = bot.get_units(UnitTypeId.SIEGETANK).amount
        self._siege_tank += bot.get_units(UnitTypeId.SIEGETANKSIEGED).amount
        self._medivac = bot.get_units(UnitTypeId.MEDIVAC).amount
        self._liberator = bot.get_units(UnitTypeId.LIBERATOR).amount
        self._liberator += bot.get_units(UnitTypeId.LIBERATORAG).amount

        mounted_marine = self._mounted.get(UnitTypeId.MARINE, 0)
        mounted_marauder = self._mounted.get(UnitTypeId.MARAUDER, 0)
        mounted_siege_tank = self._mounted.get(UnitTypeId.SIEGETANK, 0)
        mounted_medivac = self._mounted.get(UnitTypeId.MEDIVAC, 0)
        mounted_liberator = self._mounted.get(UnitTypeId.LIBERATOR, 0)

        self._attack_is_ready = True
        self._attack_is_ready &= self._marine + mounted_marine == pru.MARINE_MAX_AMOUNT
        self._attack_is_ready &= self._marauder + mounted_marauder == pru.MARAUDERS_MAX_AMOUNT
        self._attack_is_ready &= self._siege_tank + mounted_siege_tank == pru.SIEGE_TANK_MAX_AMOUNT
        self._attack_is_ready &= self._medivac + mounted_medivac == pru.MEDIVAC_MAX_AMOUNT
        self._attack_is_ready &= self._liberator + mounted_liberator == pru.LIBERATOR_MAX_AMOUNT
