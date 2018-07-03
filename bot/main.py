import asyncio
import json
from pathlib import Path

import sc2

from .agent import *


class StarPruuuft(sc2.BotAI):
    with open(Path(__file__).parent / "../botinfo.json") as f:
        NAME = json.load(f)["name"]

    def __init__(self):
        self._agents = []

    def on_start(self):
        self._agents.append(BaseAgent(self))
        self._agents.append(WorkerAgent(self))
        self._agents.append(BuilderAgent(self))
        self._agents.append(StrategyAgent(self))

    async def on_step(self, iteration):
        loop = asyncio.get_event_loop()
        tasks = []
        for agent in self._agents:
            tasks.append(loop.create_task(agent.on_step(self, iteration)))
        done, pending = await asyncio.wait(tasks, timeout=2.0)
        for task in pending:
            task.cancel()
