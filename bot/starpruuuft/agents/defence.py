from math import pi

from sc2.constants import *
from sc2.position import Point2

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent


class DefenceAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self.add_message_handler(AgentMessage.ATTACKING, self._handle_attacking)

        self._upper = None
        self._center = None
        self._near_ramp = set()
        self._structures = [
            UnitTypeId.COMMANDCENTER,
            UnitTypeId.ORBITALCOMMAND,
            UnitTypeId.BARRACKS,
            UnitTypeId.BARRACKSTECHLAB,
            UnitTypeId.BARRACKSREACTOR,
            UnitTypeId.FACTORY,
            UnitTypeId.FACTORYTECHLAB,
            UnitTypeId.STARPORT,
            UnitTypeId.STARPORTREACTOR,
            UnitTypeId.REFINERY,
            UnitTypeId.SUPPLYDEPOT,
            UnitTypeId.SUPPLYDEPOTLOWERED]
        self._militars = [
            UnitTypeId.SIEGETANK,
            UnitTypeId.LIBERATOR,
            UnitTypeId.MARAUDER,
            UnitTypeId.MEDIVAC,
            UnitTypeId.MARINE]

        self._attacking = False

    async def on_step(self, bot, iteration):
        for unit_type in self._militars:
            await self._defence(bot, unit_type)
        await self._transform_siege(bot)
        # await _under_attack(self, bot)

    def _get_points(self, bot):
        points = bot.main_base_ramp.points
        minx = min(p.x for p in points)
        miny = min(p.y for p in points)
        maxx = max(p.x for p in points)
        maxy = max(p.y for p in points)
        return Point2(((maxx+minx)/2, (maxy+miny)/2))

    async def _defence(self, bot, unit_type):
        if self._upper is None or self._center is None:
            x_axis = [max({p.x for p in d}) for d in bot.main_base_ramp.top_wall_depos]
            y_axis = [min({p.y for p in d}) for d in bot.main_base_ramp.top_wall_depos]
            self._upper = Point2((sum(x_axis)/len(x_axis), sum(y_axis)/len(y_axis)))
            self._center = self._get_points(bot)
        for unit in bot.units(unit_type).idle:
            if unit.tag not in self._near_ramp:
                position = self._center.towards_with_random_angle(self._upper, distance=7, max_difference=(pi/4))
                await bot.do(unit.move(position))
                self._near_ramp.add(unit.tag)

    async def _transform_siege(self, bot):
        for unit in bot.units(UnitTypeId.SIEGETANK).idle:
            if unit.tag in self._near_ramp and unit.tag:
                try:
                    await bot.do(unit(AbilityId.SIEGEMODE_SIEGEMODE))
                except AssertionError:
                    pass

    # async def _under_attack(self, bot):
    #     units = []
    #     for unit_type in self._structures:
    #         units |= bot.get_units(unit_type)
    #     enemy = utilities.any_enemies_near_location(bot, units, pru.SUPPLY_DEPOT_DANGER_DISTANCE)
    #     for unit_type in self._militars:
    #         for unit in bot.get_units(unit_type):
    #             await bot.do(unit.move(enemy))
