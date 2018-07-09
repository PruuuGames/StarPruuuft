import asyncio
import json
from pathlib import Path

import sc2
from sc2.units import Units
from sc2.constants import AbilityId

from .starpruuuft import StrategyAgent
from .starpruuuft import BaseAgent
from .starpruuuft import BuilderAgent
from .starpruuuft import WorkerAgent
from .starpruuuft import UpgradeAgent
from .starpruuuft import MilitarAgent
from .starpruuuft import DefenceAgent
from .starpruuuft import AttackAgent


class MyBot(sc2.BotAI):
    with open(Path(__file__).parent / "../botinfo.json") as f:
        NAME = json.load(f)["name"]

    def __init__(self):
        self.agents = {}

        self._unit_by_tag = {}
        self._units_ready = {}
        self._units_not_ready = {}
        self._pending_orders = {}

    def add_agent(self, agent_):
        self.agents[agent_.name()] = agent_

    def get_unit(self, tag):
        return self._unit_by_tag[tag]

    # Retorna a lista de unidades com o tipo escolhido ou uma lista vazia
    def get_units(self, unit_types, ready=True):
        result = []

        if not isinstance(unit_types, list):
            unit_types = [unit_types]

        for unit_type in unit_types:
            if ready and unit_type in self._units_ready:
                    result.extend(self._units_ready[unit_type])
            elif not ready and unit_type in self._units_not_ready:
                    result.extend(self._units_not_ready[unit_type])

        return Units(result, self._game_data)

    def get_pending_orders(self, ability_type):
        if ability_type not in self._pending_orders:
            return 0
        else:
            return self._pending_orders[ability_type]

    def on_start(self):
        self.add_agent(StrategyAgent(self))
        self.add_agent(BaseAgent(self))
        self.add_agent(BuilderAgent(self))
        self.add_agent(WorkerAgent(self))
        self.add_agent(UpgradeAgent(self))
        self.add_agent(MilitarAgent(self))
        self.add_agent(DefenceAgent(self))
        self.add_agent(AttackAgent(self))

    async def on_step(self, iteration):
        self._update_units_count()

        loop = asyncio.get_event_loop()
        tasks = []
        for agent_ in self.agents.values():
            tasks.append(loop.create_task(agent_.agent_step(self, iteration)))
        done, pending = await asyncio.wait(tasks, timeout=2.0)
        for task in pending:
            task.cancel()

    def _update_units_count(self):
        self._unit_by_tag = {}
        self._units_ready = {}
        self._units_not_ready = {}
        self._pending_orders = {}

        # Prepara a lista normal das unidades
        for unit in self.units:
            self._unit_by_tag[unit.tag] = unit

            if not unit.is_mine:
                continue

            unit_type = unit.type_id

            if unit_type not in self._units_ready:
                self._units_ready[unit_type] = []
                self._units_not_ready[unit_type] = []

            if unit.is_ready:
                self._units_ready[unit_type].append(unit)

                if unit.is_structure:
                    for order in unit.orders:
                        ability = order.ability.id
                        if ability not in self._pending_orders:
                            self._pending_orders[ability] = 1
                        else:
                            self._pending_orders[ability] += 1
            else:
                self._units_not_ready[unit_type].append(unit)
