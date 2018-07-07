import asyncio
import json
from pathlib import Path

import sc2

from .agent import *


class MyBot(sc2.BotAI):
    with open(Path(__file__).parent / "../botinfo.json") as f:
        NAME = json.load(f)["name"]

    def __init__(self):
        self.agents = {}

    def add_agent(self, agent):
        self.agents[agent.name()] = agent

    def on_start(self):
        self.add_agent(StrategyAgent(self))
        self.add_agent(BaseAgent(self))
        self.add_agent(BuilderAgent(self))
        self.add_agent(WorkerAgent(self))
        self.add_agent(UpgradeAgent(self))

    async def on_step(self, iteration):
        loop = asyncio.get_event_loop()
        tasks = []
        for agent in self.agents.values():
            tasks.append(loop.create_task(agent.on_step(self, iteration)))
        done, pending = await asyncio.wait(tasks, timeout=2.0)
        for task in pending:
            task.cancel()
