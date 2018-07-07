from sc2.constants import UnitTypeId


def is_command_center(unit):
    unit_type = unit.type_id
    right_type = unit_type is UnitTypeId.COMMANDCENTER or unit_type is UnitTypeId.ORBITALCOMMAND
    return unit.is_mine and right_type


def get_command_center(bot):
    command_center = bot.units().filter(lambda unit: is_command_center(unit))
    return command_center.first
