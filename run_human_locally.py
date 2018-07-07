import json

from sc2 import run_game, maps, Race
from sc2.player import Bot

from bot import MyBot


def main():
    with open("botinfo.json") as f:
        info = json.load(f)

    race = Race[info["race"]]

    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Zerg, Dummy()),
        Bot(race, MyBot())
    ], realtime=True, game_time_limit=(60*10), save_replay_as="test.SC2Replay")


if __name__ == '__main__':
    main()
