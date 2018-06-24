class Agent:
    def __init__(self, bot):
        self._bot = bot

    async def on_step(self, bot, iteration):
        raise NotImplementedError
