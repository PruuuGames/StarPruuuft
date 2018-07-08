from sc2.constants import *
from sc2.position import Point2

from bot.starpruuuft.agent_message import AgentMessage
from .agent import Agent
from .. import utilities, constants as pru


class BuilderAgent(Agent):
    def __init__(self, bot):
        super().__init__(bot)

        self.add_message_handler(AgentMessage.ENEMIES_CLOSE, self._handle_enemies_near)

        self._tracked_depots = []
        self._depots_locations = None
        self._supply_depots_raised = False

        self._supply_depot_count = 0
        self._refineries = None

        self._barracks_clear = None
        self._barracks_tech = None
        self._barracks_reactor = None
        self._factory_clear = None
        self._factory_tech = None
        self._starport_clear = None
        self._starport_reactor = None

        self._marine = 0

        self._notified = False

    async def on_step(self, bot, iteration):
        # Roda apenas uma vez
        if self._depots_locations is None:
            self._setup_depos(bot)

        # Caso não exista CC, o agente não faz nada
        cc = utilities.get_command_center(bot)
        if cc is None:
            return

        if self._barracks_clear is not None and not self._notified:
            self._notified = True
            self.send("BaseAgent", AgentMessage.BARRACKS_READY)

        await self._build_supply_depot(bot, cc)
        await self._build_refinery(bot, cc)
        await self._build_barracks(bot, cc)
        await self._build_barracks_tech(bot)
        await self._build_barracks_reactor(bot)
        await self._build_factory(bot)
        await self._build_factory_tech(bot)
        await self._build_starport(bot)
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

    def is_ramp_supply_depot(self, depot):
        return min([depot.position.to2.distance_to(depot_location) for depot_location in self._depots_locations]) <= 2

    async def _build_supply_depot(self, bot, cc):
        depots = bot.get_units([UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED])
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
        if self._barracks_clear is not None or self._barracks_tech is not None:
            enough_depots = depot_count >= 3

        if enough_depots and bot.supply_left > 4:
            return

        # Constroi um supply depot
        if bot.already_pending(UnitTypeId.SUPPLYDEPOT) < 1 and bot.can_afford(UnitTypeId.SUPPLYDEPOT):
            if depot_count < len(self._depots_locations):
                depot_location = list(self._depots_locations)[depot_count]
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=depot_location, max_distance=2, placement_step=1)
            else:
                await bot.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(
                        bot.game_info.map_center, -20))

    async def _build_refinery(self, bot, cc):
        if self._refineries.amount >= 2:
            return

        if self._barracks_clear is None and self._barracks_tech is None:
            return

        # Permite a construção de até 2 refinarias por vez
        if bot.can_afford(UnitTypeId.REFINERY):
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
        if self._barracks_clear is not None:
            return

        if self._supply_depot_count < 1:
            return

        if self._barracks_tech is not None and self._starport_reactor is None:
            return

        if self._barracks_tech is not None and self._barracks_reactor is not None:
            return

        if bot.already_pending(UnitTypeId.BARRACKS) < 1 and bot.can_afford(UnitTypeId.BARRACKS):
            if self._barracks_tech is not None:
                await bot.build(UnitTypeId.BARRACKS, near=cc.position.towards(
                        bot.game_info.map_center, 10))
            else:
                await bot.build(UnitTypeId.BARRACKS, near=cc.position.towards(
                        bot.game_info.map_center, 5))

    async def _build_barracks_tech(self, bot):
        if self._barracks_tech is not None or self._barracks_clear is None:
            return

        if self._barracks_clear is None or self._marine < pru.MARINE_INITIAL_AMOUNT:
            return

        if bot.already_pending(UnitTypeId.BARRACKSTECHLAB) < 1 and bot.can_afford(UnitTypeId.BARRACKSTECHLAB):
            await bot.do(self._barracks_clear.build(UnitTypeId.BARRACKSTECHLAB))

    async def _build_barracks_reactor(self, bot):
        if self._barracks_reactor is not None or self._barracks_clear is None:
            return

        if self._starport_reactor is None:
            return

        if bot.already_pending(UnitTypeId.BARRACKSREACTOR) < 1 and bot.can_afford(UnitTypeId.BARRACKSREACTOR):
            await bot.do(self._barracks_clear.build(UnitTypeId.BARRACKSREACTOR))

    async def _build_factory(self, bot):
        if self._factory_clear is not None or self._factory_tech is not None:
            return

        if self._barracks_tech is None or self._marine < pru.MARINE_INITIAL_AMOUNT:
            return

        if bot.already_pending(UnitTypeId.FACTORY) < 1 and bot.can_afford(UnitTypeId.FACTORY):
            await bot.build(UnitTypeId.FACTORY, near=self._refineries[0].position.towards(
                        bot.game_info.map_center, 5), max_distance=10)

    async def _build_factory_tech(self, bot):
        if self._factory_tech is not None:
            return

        if self._factory_clear is None:
            return

        if bot.already_pending(UnitTypeId.FACTORYTECHLAB) < 1 and bot.can_afford(UnitTypeId.FACTORYTECHLAB):
            await bot.do(self._factory_clear.build(UnitTypeId.FACTORYTECHLAB))

    async def _build_starport(self, bot):
        if self._starport_clear is not None or self._starport_reactor is not None:
            return

        if self._factory_clear is None or self._barracks_tech is None:
            return

        if bot.already_pending(UnitTypeId.STARPORT) < 1 and bot.can_afford(UnitTypeId.STARPORT):
            await bot.build(UnitTypeId.STARPORT, near=self._refineries[1].position.towards(
                        bot.game_info.map_center, 5), max_distance=10)

    async def _build_starport_reactor(self, bot):
        if self._starport_reactor is not None:
            return

        if self._starport_clear is None:
            return

        if bot.already_pending(UnitTypeId.STARPORTREACTOR) < 1 and bot.can_afford(UnitTypeId.STARPORTREACTOR):
            await bot.do(self._starport_clear.build(UnitTypeId.STARPORTREACTOR))

    def _cache(self, bot):
        self._barracks_clear, self._barracks_tech, self._barracks_reactor = utilities.get_barracks(bot)
        self._factory_clear, self._factory_tech = utilities.get_factory(bot)
        self._starport_clear, self._starport_reactor = utilities.get_starport(bot)

        self._supply_depot_count = bot.get_units([UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED]).amount
        self._refineries = bot.get_units(UnitTypeId.REFINERY) | bot.get_units(UnitTypeId.REFINERY, ready=False)

        self._marine = bot.get_units(UnitTypeId.MARINE).amount
