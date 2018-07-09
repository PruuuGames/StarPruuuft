from sc2.constants import *
from sc2.position import Point2
from math import pi

from .agent import Agent
from .. import utilities, constants as pru


class DefenceAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)
        self._upper = None
        self._center = None
        self._sieged = set()
        self._near_ramp = set()

    async def on_step(self, bot, iteration):
        await self._defence(bot, UnitTypeId.SIEGETANK)
        await self._defence(bot, UnitTypeId.LIBERATOR)
        await self._defence(bot, UnitTypeId.MARAUDER)
        await self._defence(bot, UnitTypeId.MEDIVAC)
        await self._defence(bot, UnitTypeId.MARINE)
        await self._transform_siege(bot)

    def _get_points(self, bot):
        points = bot.main_base_ramp.points
        minx = min(p.x for p in points)
        miny = min(p.y for p in points)
        maxx = max(p.x for p in points)
        maxy = max(p.y for p in points)
        return Point2(((maxx+minx)/2, (maxy+miny)/2))
        
    async def _defence(self, bot, unit_type):
        if self._upper is None or self._center is None:
            x_axis = [ max({p.x for p in d}) for d in bot.main_base_ramp.top_wall_depos ]
            y_axis = [ min({p.y for p in d}) for d in bot.main_base_ramp.top_wall_depos ]
            self._upper = Point2((sum(x_axis)/len(x_axis), sum(y_axis)/len(y_axis)))
            self._center = self._get_points(bot)
        for unit in bot.units(unit_type).idle:
            if unit.tag not in self._near_ramp:
                position = self._center.towards_with_random_angle(self._upper, distance=7, max_difference=(pi/4))
                await bot.do(unit.move(position))
                self._near_ramp.add(unit.tag)

    async def _transform_siege(self, bot):
        for unit in bot.units(UnitTypeId.SIEGETANK).idle:
            if unit.tag in self._near_ramp and unit.tag not in self._sieged:
                try:
                    await bot.do(unit(AbilityId.SIEGEMODE_SIEGEMODE))
                    self._sieged.add(unit.tag)
                except AssertionError:
                    pass




# self._depots_locations = [
#     Point2((max({p.x for p in d}), min({p.y for p in d})))
#     for d in bot.main_base_ramp.top_wall_depos
# ]

# [(147, 26), (146, 24), (144, 23)]

