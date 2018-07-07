import logging


class Agent:
    def __init__(self, bot):
        logging.basicConfig(format='%(asctime)s:%(message)s')
        self._info = logging.info

        self._bot = bot
        self._messages = []

    def name(self):
        return self.__class__.__name__

    def log(self, msg):
        self._info('{class_name}:{msg}'.format(class_name=self.name(), msg=msg))

    def queue_message(self, message_type, *args):
        self._messages.append((message_type, args))

    def send(self, targets, message_type, *args):
        if not isinstance(targets, list):
            targets = [targets]

        if targets is None:
            agents = self._bot.agents.values()
        else:
            agents = [self._bot.agents[target] for target in targets]

        for agent in agents:
            agent.queue_message(message_type, *args)

    def broadcast(self, message_type, *args):
        self.send(None, message_type, *args)

    async def on_step(self, bot, iteration):
        raise NotImplementedError

    async def agent_step(self, bot, iteration):
        self._process_messages()
        await self.on_step(bot, iteration)
