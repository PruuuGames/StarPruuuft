import sc2
from sc2.constants import *
from sc2.position import Point2

from bot.agent_message import AgentMessage
from .agent import Agent


class BuilderAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self._tracked_depots = []
        self._depots_locations = None
        self._raised = False

        self._supply_depots = 0
        self._barracks = 0
        self._refinery = 0
        self._barracks_tech = 0
        self._barracks_reactor = 0
        self._factory = 0
        self._factory_tech = 0
        self._starport = 0
        self._starport_reactor = 0

        self._upgrade_command_center_ready = False

    def _process_messages(self):
        if len(self._messages) == 0:
            return

        for message in self._messages:
            message_type = message[0]

            if message_type is AgentMessage.SUPPLY_DEPOTS_RAISED:
                self._raised = message[1][0]

        self._messages = []

    def _setup_depos(self, bot):
        self._depots_locations = [
            Point2((max({p.x for p in d}), min({p.y for p in d})))
            for d in bot.main_base_ramp.top_wall_depos
        ]

    def is_ramp_supply_depot(self, depot):
        return min([depot.position.to2.distance_to(depot_location) for depot_location in self._depots_locations]) <= 2

    async def _build_supply_depot(self, bot, cc):
        depots = (bot.units(UnitTypeId.SUPPLYDEPOT).ready | bot.units(UnitTypeId.SUPPLYDEPOTLOWERED).ready)
        depot_count = depots.amount

        not_tracked_depots = [depot for depot in depots if depot.tag not in self._tracked_depots]

        for depot in not_tracked_depots:
            self._tracked_depots.append(depot.tag)
            self._supply_depots += 1

            if self.is_ramp_supply_depot(depot):
                self.send("StrategyAgent", AgentMessage.RAMP_SUPPLY_DEPOT, depot.tag)

                if self._raised and depot.type_id is UnitTypeId.SUPPLYDEPOTLOWERED:
                    await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE))
                elif not self._raised and depot.type_id is UnitTypeId.SUPPLYDEPOT:
                    await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))
            elif depot.type_id == UnitTypeId.SUPPLYDEPOT:
                await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

        enough_depots = depot_count >= 1
        if self._barracks > 0:
            enough_depots = depot_count >= 3
        if enough_depots and bot.supply_left > 4:
            return

        if not bot.already_pending(UnitTypeId.SUPPLYDEPOT) and bot.can_afford(UnitTypeId.SUPPLYDEPOT):
            if depot_count < len(self._depots_locations):
                depot_location = list(self._depots_locations)[depot_count]
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=depot_location, max_distance=2, placement_step=1)
            else:
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(
                        bot.game_info.map_center, 4))

    async def _build_barracks(self, bot, cc):
        enough_barracks = self._barracks > 0
        if self._starport > 0:
            enough_barracks = self._barracks > 1
        if enough_barracks or self._supply_depots == 0:
            return

        self._barracks = bot.units(UnitTypeId.BARRACKS).ready.amount
        if not self._upgrade_command_center_ready and self._barracks == 1:
            self._upgrade_command_center_ready = True
            self.send("UpgradeAgent", AgentMessage.UPGRADE_COMMAND_CENTER_READY)
        enough_barracks = self._barracks > 0
        if self._starport > 0:
            enough_barracks = self._barracks > 1
        if enough_barracks:
            return

        if not bot.already_pending(UnitTypeId.BARRACKS) and bot.can_afford(UnitTypeId.BARRACKS):
            await bot.build(UnitTypeId.BARRACKS, near=cc.position.towards(bot.game_info.map_center, 6))

    async def _build_barracks_tech(self, bot):
        if self._barracks_tech > 0 or self._barracks == 0:
            return

        self._barracks_tech = bot.units(UnitTypeId.BARRACKSTECHLAB).ready.amount
        if self._barracks_tech > 0:
            return

        for barrack in bot.units(UnitTypeId.BARRACKS).ready:
            if barrack.add_on_tag == 0 and not bot.already_pending(UnitTypeId.BARRACKSTECHLAB) and bot.can_afford(
                    UnitTypeId.BARRACKSTECHLAB):
                await bot.do(barrack.build(UnitTypeId.BARRACKSTECHLAB))

    async def _build_barracks_reactor(self, bot):
        if self._barracks_reactor > 0 or self._barracks < 2:
            return

        self._barracks_reactor = bot.units(UnitTypeId.BARRACKSREACTOR).ready.amount
        if self._barracks_reactor > 0:
            return

        for barrack in bot.units(UnitTypeId.BARRACKS).ready:
            if barrack.add_on_tag == 0 and not bot.already_pending(UnitTypeId.BARRACKSREACTOR) and bot.can_afford(
                    UnitTypeId.BARRACKSREACTOR):
                await bot.do(barrack.build(UnitTypeId.BARRACKSREACTOR))

    async def _build_refinery(self, bot, cc):
        if self._barracks < 1 or self._refinery >= 2:
            return

        self._refinery = bot.units(UnitTypeId.REFINERY).ready.amount
        if self._refinery >= 2:
            return

        if bot.already_pending(UnitTypeId.REFINERY) <= 1 and bot.can_afford(UnitTypeId.REFINERY):
            vgs = bot.state.vespene_geyser.closer_than(20.0, cc)
            for vg in vgs:
                if bot.units(UnitTypeId.REFINERY).closer_than(1.0, vg).exists:
                    break

                worker = bot.select_build_worker(vg.position)
                if worker is None:
                    break

                await bot.do(worker.build(UnitTypeId.REFINERY, vg))
                break

    async def _build_factory(self, bot, cc):
        if self._factory > 0 or self._barracks == 0:
            return

        self._factory = bot.units(UnitTypeId.FACTORY).ready.amount
        if self._factory > 0:
            return

        if not bot.already_pending(UnitTypeId.FACTORY) and bot.can_afford(UnitTypeId.FACTORY):
            await bot.build(UnitTypeId.FACTORY, near=cc.position.towards(bot.game_info.map_center, 8))

    async def _build_factory_tech(self, bot):
        if self._factory_tech > 0 or self._factory == 0:
            return

        self._factory_tech = bot.units(UnitTypeId.FACTORYTECHLAB).ready.amount
        if self._factory_tech > 0:
            return

        for factory in bot.units(UnitTypeId.FACTORY).ready:
            if factory.add_on_tag == 0 and not bot.already_pending(UnitTypeId.FACTORYTECHLAB) and bot.can_afford(
                    UnitTypeId.FACTORYTECHLAB):
                await bot.do(factory.build(UnitTypeId.FACTORYTECHLAB))

    async def _build_starport(self, bot, cc):
        if self._starport > 0 or self._factory == 0:
            return

        self._starport = bot.units(UnitTypeId.STARPORT).ready.amount
        if self._starport > 0:
            return

        if not bot.already_pending(UnitTypeId.STARPORT) and bot.can_afford(UnitTypeId.STARPORT):
            await bot.build(UnitTypeId.STARPORT, near=cc.position.towards(bot.game_info.map_center, 10))

    async def _build_starport_reactor(self, bot):
        if self._starport_reactor > 0 or self._starport == 0:
            return

        self._starport_reactor = bot.units(UnitTypeId.STARPORTREACTOR).ready.amount
        if self._starport_reactor > 0:
            return

        for starport in bot.units(UnitTypeId.STARPORT).ready:
            if starport.add_on_tag == 0 and not bot.already_pending(UnitTypeId.STARPORTREACTOR) and bot.can_afford(
                    UnitTypeId.STARPORTREACTOR):
                await bot.do(starport.build(UnitTypeId.STARPORTREACTOR))

    async def on_step(self, bot, iteration):
        """
        :param sc2.BotAI bot:
        :param iteration:
        """

        self._process_messages()

        if self._depots_locations is None:
            self._setup_depos(bot)

        cc = (bot.units(UnitTypeId.COMMANDCENTER) | bot.units(UnitTypeId.ORBITALCOMMAND)).ready
        if not cc.exists:
            return
        else:
            cc = cc.first

        await self._build_supply_depot(bot, cc)
        await self._build_barracks(bot, cc)
        await self._build_refinery(bot, cc)
        await self._build_barracks_tech(bot)
        await self._build_factory(bot, cc)
        await self._build_factory_tech(bot)
        await self._build_starport(bot, cc)
        await self._build_starport_reactor(bot)
        await self._build_barracks_reactor(bot)
