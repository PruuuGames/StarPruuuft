import logging


class Agent:
    def __init__(self, bot):
        self._bot = bot

        logging.basicConfig(format='%(asctime)s:%(message)s')
        self._info = logging.info

    def log(self, msg):
        self._info('{class_name}:{msg}'.format(class_name=self, msg=msg))

    async def on_step(self, bot, iteration):
        raise NotImplementedError
