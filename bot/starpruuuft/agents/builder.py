from sc2.constants import *
from sc2.position import Point2

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent
from .. import utilities


class BuilderAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self.add_message_handler(AgentMessage.ENEMIES_CLOSE, self._handle_enemies_near)

        self._tracked_depots = []
        self._depots_locations = None
        self._supply_depots_raised = False

        self._supply_depot = 0
        self._refinery = 0
        self._barracks = 0
        self._barracks_tech = 0
        self._barracks_reactor = 0;
        self._factory = 0
        self._factory_tech = 0
        self._starport = 0
        self._starport_reactor = 0

        self._notified = False

    async def on_step(self, bot, iteration):
        # Roda apenas uma vez
        if self._depots_locations is None:
            self._setup_depos(bot)

        # Caso não exista CC, o agente não faz nada
        cc = utilities.get_command_center(bot)
        if cc is None:
            return

        self._update_counts(bot)

        if self._barracks > 0 and not self._notified:
            self._notified = True
            self.send("BaseAgent", AgentMessage.BARRACKS_READY)

        await self._build_supply_depot(bot, cc)
        await self._build_refinery(bot, cc)
        await self._build_barracks(bot, cc)
        await self._build_barracks_tech(bot)
        await self._build_barracks_reactor(bot)
        await self._build_factory(bot, cc)
        await self._build_factory_tech(bot)
        await self._build_starport(bot, cc)
        await self._build_starport_reactor(bot)

    # Reconhece um depot localizado na rampa
    def _handle_enemies_near(self, *args):
        self._supply_depots_raised = args[0]

    # Faz o cache da localização dos depots de rampa
    def _setup_depos(self, bot):
        self._depots_locations = [
            Point2((max({p.x for p in d}), min({p.y for p in d})))
            for d in bot.main_base_ramp.top_wall_depos
        ]

    # Atualiza a contagem de estruturas
    def _update_counts(self, bot):
        units = bot.units

        self._supply_depot = units.filter(lambda unit: utilities.is_supply_depot(unit)).amount
        self._refinery = units.filter(lambda unit: utilities.is_refinery(unit)).amount
        self._barracks = units.filter(lambda unit: utilities.is_barracks(unit)).amount
        self._barracks_tech = units.filter(lambda unit: utilities.is_barracks_tech_lab(unit)).amount
        self._barracks_reactor = units.filter(lambda unit: utilities.is_barracks_reactor(unit)).amount
        self._factory = units.filter(lambda unit: utilities.is_factory(unit)).amount
        self._factory_tech = units.filter(lambda unit: utilities.is_factory_tech_lab(unit)).amount
        self._starport = units.filter(lambda unit: utilities.is_starport(unit)).amount
        self._starport_reactor = units.filter(lambda unit: utilities.is_starport_reactor(unit)).amount

    def is_ramp_supply_depot(self, depot):
        return min([depot.position.to2.distance_to(depot_location) for depot_location in self._depots_locations]) <= 2

    async def _build_supply_depot(self, bot, cc):
        depots = bot.units.filter(lambda unit: utilities.is_supply_depot(unit))
        depot_count = depots.amount

        # Marca os supply depots recém finalizados
        not_tracked_depots = [depot for depot in depots if depot.tag not in self._tracked_depots]
        for depot in not_tracked_depots:
            self._tracked_depots.append(depot.tag)

            if self.is_ramp_supply_depot(depot):
                self.send("StrategyAgent", AgentMessage.RAMP_SUPPLY_DEPOT, depot.tag)

                # Ajusta o estado do supply depot de acordo com a presença de inimigos
                if self._supply_depots_raised and depot.type_id is UnitTypeId.SUPPLYDEPOTLOWERED:
                    await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE))
                elif not self._supply_depots_raised and depot.type_id is UnitTypeId.SUPPLYDEPOT:
                    await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))
            elif depot.type_id == UnitTypeId.SUPPLYDEPOT:
                # Supply depots que não estão na rampa devem estar abaixados
                await bot.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))

        # Caso já existam quarteis, é necessário fechar a rampa com os 3 depots. Caso contrário, apenas 1
        enough_depots = depot_count >= 1
        if bot.units.filter(lambda unit: unit.is_ready and unit.type_id is UnitTypeId.BARRACKS).amount > 0:
            enough_depots = depot_count >= 3

        if enough_depots and bot.supply_left > 4:
            return

        # Constroi um supply depot
        if not bot.already_pending(UnitTypeId.SUPPLYDEPOT) and bot.can_afford(UnitTypeId.SUPPLYDEPOT):
            if depot_count < len(self._depots_locations):
                depot_location = list(self._depots_locations)[depot_count]
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=depot_location, max_distance=2, placement_step=1)
            else:
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(
                        bot.game_info.map_center, 4))

    async def _build_refinery(self, bot, cc):
        if self._barracks < 1 or self._refinery >= 2:
            return

        # Permite a construção de até 2 refinarias por vez
        if bot.already_pending(UnitTypeId.REFINERY) + self._refinery <= 2 and bot.can_afford(UnitTypeId.REFINERY):
            vgs = bot.state.vespene_geyser.closer_than(20.0, cc)
            for vg in vgs:
                if bot.units(UnitTypeId.REFINERY).closer_than(1.0, vg).exists:
                    break

                worker = bot.select_build_worker(vg.position)
                if worker is None:
                    break

                await bot.do(worker.build(UnitTypeId.REFINERY, vg))
                break

    async def _build_barracks(self, bot, cc):
        # Caso já exista starport, deve construir a barracks secundária
        enough_barracks = self._barracks > 0
        if self._starport > 0:
            enough_barracks = self._barracks > 1
        if enough_barracks or self._supply_depot < 1:
            return

        if not bot.already_pending(UnitTypeId.BARRACKS) and bot.can_afford(UnitTypeId.BARRACKS):
            await bot.build(UnitTypeId.BARRACKS, near=cc.position.towards(bot.game_info.map_center, 6))

    async def _build_barracks_tech(self, bot):
        if self._barracks_tech > 0 or self._barracks == 0:
            return

        for barrack in bot.units(UnitTypeId.BARRACKS).ready:
            if barrack.add_on_tag == 0 and not bot.already_pending(UnitTypeId.BARRACKSTECHLAB) and bot.can_afford(
                    UnitTypeId.BARRACKSTECHLAB):
                await bot.do(barrack.build(UnitTypeId.BARRACKSTECHLAB))
                break

    async def _build_barracks_reactor(self, bot):
        if self._barracks_reactor > 0 or self._barracks < 2:
            return

        for barrack in bot.units(UnitTypeId.BARRACKS).ready:
            if barrack.add_on_tag == 0 and not bot.already_pending(UnitTypeId.BARRACKSREACTOR) and bot.can_afford(
                    UnitTypeId.BARRACKSREACTOR):
                await bot.do(barrack.build(UnitTypeId.BARRACKSREACTOR))
                break

    async def _build_factory(self, bot, cc):
        if self._factory > 0 or self._barracks == 0:
            return

        if not bot.already_pending(UnitTypeId.FACTORY) and bot.can_afford(UnitTypeId.FACTORY):
            await bot.build(UnitTypeId.FACTORY, near=cc.position.towards(bot.game_info.map_center, 8))

    async def _build_factory_tech(self, bot):
        if self._factory_tech > 0 or self._factory == 0:
            return

        for factory in bot.units(UnitTypeId.FACTORY).ready:
            if factory.add_on_tag == 0 and not bot.already_pending(UnitTypeId.FACTORYTECHLAB) and bot.can_afford(
                    UnitTypeId.FACTORYTECHLAB):
                await bot.do(factory.build(UnitTypeId.FACTORYTECHLAB))
                break

    async def _build_starport(self, bot, cc):
        if self._starport > 0 or self._factory == 0:
            return

        if not bot.already_pending(UnitTypeId.STARPORT) and bot.can_afford(UnitTypeId.STARPORT):
            await bot.build(UnitTypeId.STARPORT, near=cc.position.towards(bot.game_info.map_center, 10))

    async def _build_starport_reactor(self, bot):
        if self._starport_reactor > 0 or self._starport == 0:
            return

        for starport in bot.units(UnitTypeId.STARPORT).ready:
            if starport.add_on_tag == 0 and not bot.already_pending(UnitTypeId.STARPORTREACTOR) and bot.can_afford(
                    UnitTypeId.STARPORTREACTOR):
                await bot.do(starport.build(UnitTypeId.STARPORTREACTOR))
                break
