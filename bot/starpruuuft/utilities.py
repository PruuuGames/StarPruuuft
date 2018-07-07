from sc2.constants import UnitTypeId


def is_command_center(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.COMMANDCENTER or unit_type is UnitTypeId.ORBITALCOMMAND
    return unit.is_mine and right_type


def is_supply_depot(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.SUPPLYDEPOT or unit_type is UnitTypeId.SUPPLYDEPOTLOWERED
    return unit.is_mine and unit.is_ready and right_type


def is_refinery(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.REFINERY
    return unit.is_mine and unit.is_ready and right_type


def is_barracks(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.BARRACKS
    return unit.is_mine and unit.is_ready and right_type


def is_barracks_tech_lab(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.BARRACKSTECHLAB
    return unit.is_mine and unit.is_ready and right_type


def is_barracks_reactor(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.BARRACKSREACTOR
    return unit.is_mine and unit.is_ready and right_type


def is_factory(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.FACTORY
    return unit.is_mine and unit.is_ready and right_type


def is_factory_tech_lab(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.FACTORYTECHLAB
    return unit.is_mine and unit.is_ready and right_type


def is_starport(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.STARPORT
    return unit.is_mine and unit.is_ready and right_type


def is_starport_reactor(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.STARPORTREACTOR
    return unit.is_mine and unit.is_ready and right_type


def get_command_center(bot):
    command_center = bot.units().filter(lambda unit: is_command_center(unit))

    if command_center.exists:
        return command_center.first
    else:
        return None


def any_enemies_near(bot, units, distance):
    enemy_units = bot.known_enemy_units.not_structure

    for enemy in enemy_units:
        for unit in units:
            if unit.position.to2.distance_to(enemy.position.to2) <= distance:
                return True

    return False
