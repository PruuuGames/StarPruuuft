from sc2.constants import UnitTypeId
from sc2.position import Point2


def is_type(unit, unit_types, mine=True, ready=True):
    if (mine and not unit.is_mine) or (not mine and unit.is_mine):
        return False

    if (ready and not unit.is_ready) or (not ready and unit.is_ready):
        return False

    if not isinstance(unit_types, list):
        unit_types = [unit_types]

    return any(unit.type_id is unit_type for unit_type in unit_types)


def is_command_center(unit):
    return is_type(unit, [UnitTypeId.COMMANDCENTER, UnitTypeId.ORBITALCOMMAND])


def get_command_center(bot):
    command_center = bot.get_units([UnitTypeId.COMMANDCENTER, UnitTypeId.ORBITALCOMMAND])

    if command_center.exists:
        return command_center.first
    else:
        return None


def get_barracks(bot, ready=True):
    barracks_clear = None
    barracks_tech = None
    barracks_reactor = None

    units = bot.get_units(UnitTypeId.BARRACKS)
    if not ready:
        units = units | bot.get_units(UnitTypeId.BARRACKS, ready=False)
    for barracks in units:
        if barracks.add_on_tag == 0:
            barracks_clear = barracks
        else:
            extension = bot.get_unit(barracks.add_on_tag)

            if extension.is_ready:
                if extension.type_id is UnitTypeId.BARRACKSTECHLAB:
                    barracks_tech = barracks
                elif extension.type_id is UnitTypeId.BARRACKSREACTOR:
                    barracks_reactor = barracks

    return barracks_clear, barracks_tech, barracks_reactor


def get_factory(bot, ready=True):
    factory_clear = None
    factory_tech = None

    units = bot.get_units(UnitTypeId.FACTORY)
    if not ready:
        units = units | bot.get_units(UnitTypeId.FACTORY, ready=False)
    for factory in units:
        if factory.add_on_tag == 0:
            factory_clear = factory
        else:
            extension = bot.get_unit(factory.add_on_tag)

            if extension.is_ready and extension.type_id is UnitTypeId.FACTORYTECHLAB:
                factory_tech = factory

    return factory_clear, factory_tech


def get_starport(bot, ready=True):
    starport_clear = None
    starport_reactor = None

    units = bot.get_units(UnitTypeId.STARPORT)
    if not ready:
        units = units | bot.get_units(UnitTypeId.STARPORTREACTOR, ready=False)
    for starport in units:
        if starport.add_on_tag == 0:
            starport_clear = starport
        else:
            extension = bot.get_unit(starport.add_on_tag)

            if extension.is_ready and extension.type_id is UnitTypeId.STARPORTREACTOR:
                starport_reactor = starport

    return starport_clear, starport_reactor


def is_done(unit):
    return unit is not None and unit.is_ready


def already_pending(bot, unit_type):
    return bot.get_units(unit_type, ready=False).exists


def get_center_relative_position(bot, structure, displacement):
    center = bot.game_info.map_center.to2
    structure = structure.position.to2

    x_diff = (displacement if center.x > structure.x else -displacement)
    y_diff = (displacement if center.y > structure.y else -displacement)

    return Point2((structure.x + x_diff, structure.y + y_diff))


def any_enemies_near(bot, units, distance):
    enemy_units = bot.known_enemy_units.not_structure

    for enemy in enemy_units:
        for unit in units:
            if unit.position.to2.distance_to(enemy.position.to2) <= distance:
                return True

    return False


def any_enemies_near_location(bot, units, distance):
    enemy_units = bot.known_enemy_units.not_structure

    for enemy in enemy_units:
        for unit in units:
            if unit.position.to2.distance_to(enemy.position.to2) <= distance:
                return enemy.position.to2
    return None

