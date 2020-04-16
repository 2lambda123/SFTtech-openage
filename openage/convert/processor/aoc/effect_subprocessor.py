# Copyright 2020-2020 the openage authors. See copying.md for legal info.

"""
Creates effects and resistances for the Apply*Effect and Resistance
abilities.
"""
from openage.convert.dataformat.aoc.internal_nyan_names import ARMOR_CLASS_LOOKUPS,\
    UNIT_LINE_LOOKUPS, BUILDING_LINE_LOOKUPS
from openage.convert.dataformat.converter_object import RawAPIObject
from openage.convert.dataformat.aoc.expected_pointer import ExpectedPointer
from openage.convert.dataformat.aoc.genie_unit import GenieUnitLineGroup


class AoCEffectSubprocessor:

    @staticmethod
    def get_attack_effects(line, ability_ref):
        """
        Creates effects that are used for attacking (unit command: 7)

        :param line: Unit/Building line that gets the ability.
        :type line: ...dataformat.converter_object.ConverterObjectGroup
        :param ability_ref: Reference of the ability raw API object the effects are added to.
        :type ability_ref: str
        :returns: The expected pointers for the effects.
        :rtype: list
        """
        current_unit = line.get_head_unit()
        dataset = line.data

        effects = []

        # FlatAttributeChangeDecrease
        effect_parent = "engine.effect.discrete.flat_attribute_change.FlatAttributeChange"
        attack_parent = "engine.effect.discrete.flat_attribute_change.type.FlatAttributeChangeDecrease"

        attacks = current_unit["attacks"].get_value()

        for attack in attacks.values():
            armor_class = attack["type_id"].get_value()
            attack_amount = attack["amount"].get_value()
            class_name = ARMOR_CLASS_LOOKUPS[armor_class]

            attack_ref = "%s.%s" % (ability_ref, class_name)
            attack_raw_api_object = RawAPIObject(attack_ref,
                                                 class_name,
                                                 dataset.nyan_api_objects)
            attack_raw_api_object.add_raw_parent(attack_parent)
            attack_location = ExpectedPointer(line, ability_ref)
            attack_raw_api_object.set_location(attack_location)

            # Type
            type_ref = "aux.attribute_change_type.types.%s" % (class_name)
            change_type = dataset.pregen_nyan_objects[type_ref].get_nyan_object()
            attack_raw_api_object.add_raw_member("type",
                                                 change_type,
                                                 effect_parent)

            # Min value (optional)
            min_value = dataset.pregen_nyan_objects[("effect.discrete.flat_attribute_change."
                                                     "min_damage.AoE2MinChangeAmount")].get_nyan_object()
            attack_raw_api_object.add_raw_member("min_change_value",
                                                 min_value,
                                                 effect_parent)

            # Max value (optional; not added because there is none in AoE2)

            # Change value
            # =================================================================================
            amount_name = "%s.%s.ChangeAmount" % (ability_ref, class_name)
            amount_raw_api_object = RawAPIObject(amount_name, "ChangeAmount", dataset.nyan_api_objects)
            amount_raw_api_object.add_raw_parent("engine.aux.attribute.AttributeAmount")
            amount_location = ExpectedPointer(line, attack_ref)
            amount_raw_api_object.set_location(amount_location)

            attribute = dataset.pregen_nyan_objects["aux.attribute.types.Health"].get_nyan_object()
            amount_raw_api_object.add_raw_member("type",
                                                 attribute,
                                                 "engine.aux.attribute.AttributeAmount")
            amount_raw_api_object.add_raw_member("amount",
                                                 attack_amount,
                                                 "engine.aux.attribute.AttributeAmount")

            line.add_raw_api_object(amount_raw_api_object)
            # =================================================================================
            amount_expected_pointer = ExpectedPointer(line, amount_name)
            attack_raw_api_object.add_raw_member("change_value",
                                                 amount_expected_pointer,
                                                 effect_parent)

            # Ignore protection
            attack_raw_api_object.add_raw_member("ignore_protection",
                                                 [],
                                                 effect_parent)

            line.add_raw_api_object(attack_raw_api_object)
            attack_expected_pointer = ExpectedPointer(line, attack_ref)
            effects.append(attack_expected_pointer)

        # Fallback effect
        fallback_effect = dataset.pregen_nyan_objects[("effect.discrete.flat_attribute_change."
                                                       "fallback.AoE2AttackFallback")].get_nyan_object()
        effects.append(fallback_effect)

        return effects

    @staticmethod
    def get_convert_effects(line, ability_ref):
        """
        Creates effects that are used for attacking (unit command: 104)

        :param line: Unit/Building line that gets the ability.
        :type line: ...dataformat.converter_object.ConverterObjectGroup
        :param ability_ref: Reference of the ability raw API object the effects are added to.
        :type ability_ref: str
        :returns: The expected pointers for the effects.
        :rtype: list
        """
        current_unit = line.get_head_unit()
        dataset = line.data

        effects = []

        effect_parent = "engine.effect.discrete.convert.Convert"
        convert_parent = "engine.effect.discrete.convert.type.AoE2Convert"

        unit_commands = current_unit.get_member("unit_commands").get_value()
        for command in unit_commands:
            # Find the Heal command.
            type_id = command.get_value()["type"].get_value()

            if type_id == 104:
                break

        else:
            # Return the empty set
            return effects

        convert_ref = "%s.ConvertEffect" % (ability_ref)
        convert_raw_api_object = RawAPIObject(convert_ref,
                                              "ConvertEffect",
                                              dataset.nyan_api_objects)
        convert_raw_api_object.add_raw_parent(convert_parent)
        convert_location = ExpectedPointer(line, ability_ref)
        convert_raw_api_object.set_location(convert_location)

        # Type
        type_ref = "aux.convert_type.types.Convert"
        change_type = dataset.pregen_nyan_objects[type_ref].get_nyan_object()
        convert_raw_api_object.add_raw_member("type",
                                              change_type,
                                              effect_parent)

        # Min success (optional; not added because there is none in AoE2)
        # Max success (optional; not added because there is none in AoE2)

        # Chance
        chance_success = 0.25   # hardcoded
        convert_raw_api_object.add_raw_member("chance_success",
                                              chance_success,
                                              effect_parent)

        # Fail cost (optional; not added because there is none in AoE2)

        # Guaranteed rounds skip
        convert_raw_api_object.add_raw_member("skip_guaranteed_rounds",
                                              0,
                                              convert_parent)

        # Protected rounds skip
        convert_raw_api_object.add_raw_member("skip_protected_rounds",
                                              0,
                                              convert_parent)

        line.add_raw_api_object(convert_raw_api_object)
        attack_expected_pointer = ExpectedPointer(line, convert_ref)
        effects.append(attack_expected_pointer)

        return effects

    @staticmethod
    def get_heal_effects(line, ability_ref):
        """
        Creates effects that are used for healing (unit command: 105)

        :param line: Unit/Building line that gets the ability.
        :type line: ...dataformat.converter_object.ConverterObjectGroup
        :param ability_ref: Reference of the ability raw API object the effects are added to.
        :type ability_ref: str
        :returns: The expected pointers for the effects.
        :rtype: list
        """
        current_unit = line.get_head_unit()
        dataset = line.data

        effects = []

        effect_parent = "engine.effect.continuous.flat_attribute_change.FlatAttributeChange"
        heal_parent = "engine.effect.continuous.flat_attribute_change.type.FlatAttributeChangeIncrease"

        unit_commands = current_unit.get_member("unit_commands").get_value()
        heal_command = None

        for command in unit_commands:
            # Find the Heal command.
            type_id = command.get_value()["type"].get_value()

            if type_id == 105:
                heal_command = command
                break

        else:
            # Return the empty set
            return effects

        heal_rate = heal_command.get_value()["work_value1"].get_value()

        heal_ref = "%s.HealEffect" % (ability_ref)
        heal_raw_api_object = RawAPIObject(heal_ref,
                                           "HealEffect",
                                           dataset.nyan_api_objects)
        heal_raw_api_object.add_raw_parent(heal_parent)
        heal_location = ExpectedPointer(line, ability_ref)
        heal_raw_api_object.set_location(heal_location)

        # Type
        type_ref = "aux.attribute_change_type.types.Heal"
        change_type = dataset.pregen_nyan_objects[type_ref].get_nyan_object()
        heal_raw_api_object.add_raw_member("type",
                                           change_type,
                                           effect_parent)

        # Min value (optional)
        min_value = dataset.pregen_nyan_objects[("effect.discrete.flat_attribute_change."
                                                 "min_heal.AoE2MinChangeAmount")].get_nyan_object()
        heal_raw_api_object.add_raw_member("min_change_rate",
                                           min_value,
                                           effect_parent)

        # Max value (optional; not added because there is none in AoE2)

        # Change rate
        # =================================================================================
        rate_name = "%s.HealEffect.ChangeRate" % (ability_ref)
        rate_raw_api_object = RawAPIObject(rate_name, "ChangeRate", dataset.nyan_api_objects)
        rate_raw_api_object.add_raw_parent("engine.aux.attribute.AttributeRate")
        rate_location = ExpectedPointer(line, heal_ref)
        rate_raw_api_object.set_location(rate_location)

        attribute = dataset.pregen_nyan_objects["aux.attribute.types.Health"].get_nyan_object()
        rate_raw_api_object.add_raw_member("type",
                                           attribute,
                                           "engine.aux.attribute.AttributeRate")
        rate_raw_api_object.add_raw_member("rate",
                                           heal_rate,
                                           "engine.aux.attribute.AttributeRate")

        line.add_raw_api_object(rate_raw_api_object)
        # =================================================================================
        rate_expected_pointer = ExpectedPointer(line, rate_name)
        heal_raw_api_object.add_raw_member("change_rate",
                                           rate_expected_pointer,
                                           effect_parent)

        # Ignore protection
        heal_raw_api_object.add_raw_member("ignore_protection",
                                           [],
                                           effect_parent)

        line.add_raw_api_object(heal_raw_api_object)
        heal_expected_pointer = ExpectedPointer(line, heal_ref)
        effects.append(heal_expected_pointer)

        return effects

    @staticmethod
    def get_repair_effects(line, ability_ref):
        """
        Creates effects that are used for repairing (unit command: 106)

        TODO: Cost

        :param line: Unit/Building line that gets the ability.
        :type line: ...dataformat.converter_object.ConverterObjectGroup
        :param ability_ref: Reference of the ability raw API object the effects are added to.
        :type ability_ref: str
        :returns: The expected pointers for the effects.
        :rtype: list
        """
        dataset = line.data

        effects = []

        effect_parent = "engine.effect.continuous.flat_attribute_change.FlatAttributeChange"
        repair_parent = "engine.effect.continuous.flat_attribute_change.type.FlatAttributeChangeIncrease"

        repairable_lines = []
        repairable_lines.extend(dataset.building_lines.values())
        for unit_line in dataset.unit_lines.values():
            if unit_line.get_class_id() in (2, 13, 20, 21, 22, 55):
                repairable_lines.append(unit_line)

        for repairable_line in repairable_lines:
            if isinstance(repairable_line, GenieUnitLineGroup):
                game_entity_name = UNIT_LINE_LOOKUPS[repairable_line.get_head_unit_id()][0]

            else:
                game_entity_name = BUILDING_LINE_LOOKUPS[repairable_line.get_head_unit_id()][0]

            repair_name = "%sRepairEffect" % (game_entity_name)
            repair_ref = "%s.%s" % (ability_ref, repair_name)
            repair_raw_api_object = RawAPIObject(repair_ref,
                                                 repair_name,
                                                 dataset.nyan_api_objects)
            repair_raw_api_object.add_raw_parent(repair_parent)
            repair_location = ExpectedPointer(line, ability_ref)
            repair_raw_api_object.set_location(repair_location)

            # Type
            type_ref = "aux.attribute_change_type.types.%sRepair" % (game_entity_name)
            change_type = dataset.pregen_nyan_objects[type_ref].get_nyan_object()
            repair_raw_api_object.add_raw_member("type",
                                                 change_type,
                                                 effect_parent)

            # Min value (optional; not added because buildings don't block repairing)

            # Max value (optional; not added because there is none in AoE2)

            # Change rate
            # =================================================================================
            rate_name = "%s.%s.ChangeRate" % (ability_ref, repair_name)
            rate_raw_api_object = RawAPIObject(rate_name, "ChangeRate", dataset.nyan_api_objects)
            rate_raw_api_object.add_raw_parent("engine.aux.attribute.AttributeRate")
            rate_location = ExpectedPointer(line, repair_ref)
            rate_raw_api_object.set_location(rate_location)

            attribute = dataset.pregen_nyan_objects["aux.attribute.types.Health"].get_nyan_object()
            rate_raw_api_object.add_raw_member("type",
                                               attribute,
                                               "engine.aux.attribute.AttributeRate")

            # Hardcoded repair rate: 750 HP/min = 12.5 HP/s
            repair_rate = 12.5
            rate_raw_api_object.add_raw_member("rate",
                                               repair_rate,
                                               "engine.aux.attribute.AttributeRate")

            line.add_raw_api_object(rate_raw_api_object)
            # =================================================================================
            rate_expected_pointer = ExpectedPointer(line, rate_name)
            repair_raw_api_object.add_raw_member("change_rate",
                                                 rate_expected_pointer,
                                                 effect_parent)

            # Ignore protection
            repair_raw_api_object.add_raw_member("ignore_protection",
                                                 [],
                                                 effect_parent)

            line.add_raw_api_object(repair_raw_api_object)
            repair_expected_pointer = ExpectedPointer(line, repair_ref)
            effects.append(repair_expected_pointer)

        return effects

    @staticmethod
    def get_construct_effects(line, ability_ref):
        """
        Creates effects that are used for construction (unit command: 101)

        :param line: Unit/Building line that gets the ability.
        :type line: ...dataformat.converter_object.ConverterObjectGroup
        :param ability_ref: Reference of the ability raw API object the effects are added to.
        :type ability_ref: str
        :returns: The expected pointers for the effects.
        :rtype: list
        """
        dataset = line.data

        effects = []

        progress_effect_parent = "engine.effect.continuous.time_relative_progress.TimeRelativeProgressChange"
        progress_construct_parent = "engine.effect.continuous.time_relative_progress.type.TimeRelativeProgressIncrease"
        attr_effect_parent = "engine.effect.continuous.time_relative_attribute.TimeRelativeAttributeChange"
        attr_construct_parent = "engine.effect.continuous.time_relative_attribute.type.TimeRelativeAttributeIncrease"

        constructable_lines = []
        constructable_lines.extend(dataset.building_lines.values())

        for constructable_line in constructable_lines:
            if isinstance(constructable_line, GenieUnitLineGroup):
                game_entity_name = UNIT_LINE_LOOKUPS[constructable_line.get_head_unit_id()][0]

            else:
                game_entity_name = BUILDING_LINE_LOOKUPS[constructable_line.get_head_unit_id()][0]

            # Construction progress
            contruct_progress_name = "%sConstructProgressEffect" % (game_entity_name)
            contruct_progress_ref = "%s.%s" % (ability_ref, contruct_progress_name)
            contruct_progress_raw_api_object = RawAPIObject(contruct_progress_ref,
                                                            contruct_progress_name,
                                                            dataset.nyan_api_objects)
            contruct_progress_raw_api_object.add_raw_parent(progress_construct_parent)
            contruct_progress_location = ExpectedPointer(line, ability_ref)
            contruct_progress_raw_api_object.set_location(contruct_progress_location)

            # Type
            type_ref = "aux.construct_type.types.%sConstruct" % (game_entity_name)
            change_type = dataset.pregen_nyan_objects[type_ref].get_nyan_object()
            contruct_progress_raw_api_object.add_raw_member("type",
                                                            change_type,
                                                            progress_effect_parent)

            # Total change time
            change_time = constructable_line.get_head_unit()["creation_time"].get_value()
            contruct_progress_raw_api_object.add_raw_member("total_change_time",
                                                            change_time,
                                                            progress_effect_parent)

            line.add_raw_api_object(contruct_progress_raw_api_object)
            contruct_progress_expected_pointer = ExpectedPointer(line, contruct_progress_ref)
            effects.append(contruct_progress_expected_pointer)

            # HP increase during construction
            contruct_hp_name = "%sConstructHPEffect" % (game_entity_name)
            contruct_hp_ref = "%s.%s" % (ability_ref, contruct_hp_name)
            contruct_hp_raw_api_object = RawAPIObject(contruct_hp_ref,
                                                      contruct_hp_name,
                                                      dataset.nyan_api_objects)
            contruct_hp_raw_api_object.add_raw_parent(attr_construct_parent)
            contruct_hp_location = ExpectedPointer(line, ability_ref)
            contruct_hp_raw_api_object.set_location(contruct_hp_location)

            # Type
            type_ref = "aux.attribute_change_type.types.%sConstruct" % (game_entity_name)
            change_type = dataset.pregen_nyan_objects[type_ref].get_nyan_object()
            contruct_hp_raw_api_object.add_raw_member("type",
                                                      change_type,
                                                      attr_effect_parent)

            # Total change time
            change_time = constructable_line.get_head_unit()["creation_time"].get_value()
            contruct_hp_raw_api_object.add_raw_member("total_change_time",
                                                      change_time,
                                                      attr_effect_parent)

            # Ignore protection
            contruct_hp_raw_api_object.add_raw_member("ignore_protection",
                                                      [],
                                                      attr_effect_parent)

            line.add_raw_api_object(contruct_hp_raw_api_object)
            contruct_hp_expected_pointer = ExpectedPointer(line, contruct_hp_ref)
            effects.append(contruct_hp_expected_pointer)

        return effects

    @staticmethod
    def get_attack_resistances(line, ability_ref):
        """
        Creates resistances that are used for attacking (unit command: 7)

        :param line: Unit/Building line that gets the ability.
        :type line: ...dataformat.converter_object.ConverterObjectGroup
        :param ability_ref: Reference of the ability raw API object the effects are added to.
        :type ability_ref: str
        :returns: The expected pointers for the effects.
        :rtype: list
        """
        current_unit = line.get_head_unit()
        dataset = line.data

        resistances = []

        # FlatAttributeChangeDecrease
        resistance_parent = "engine.resistance.discrete.flat_attribute_change.FlatAttributeChange"
        armor_parent = "engine.resistance.discrete.flat_attribute_change.type.FlatAttributeChangeDecrease"

        if current_unit.has_member("armors"):
            armors = current_unit["armors"].get_value()

        else:
            # TODO: Trees and blast defense
            armors = {}

        for armor in armors.values():
            armor_class = armor["type_id"].get_value()
            armor_amount = armor["amount"].get_value()
            class_name = ARMOR_CLASS_LOOKUPS[armor_class]

            armor_ref = "%s.%s" % (ability_ref, class_name)
            armor_raw_api_object = RawAPIObject(armor_ref, class_name, dataset.nyan_api_objects)
            armor_raw_api_object.add_raw_parent(armor_parent)
            armor_location = ExpectedPointer(line, ability_ref)
            armor_raw_api_object.set_location(armor_location)

            # Type
            type_ref = "aux.attribute_change_type.types.%s" % (class_name)
            change_type = dataset.pregen_nyan_objects[type_ref].get_nyan_object()
            armor_raw_api_object.add_raw_member("type",
                                                change_type,
                                                resistance_parent)

            # Block value
            # =================================================================================
            amount_name = "%s.%s.BlockAmount" % (ability_ref, class_name)
            amount_raw_api_object = RawAPIObject(amount_name, "BlockAmount", dataset.nyan_api_objects)
            amount_raw_api_object.add_raw_parent("engine.aux.attribute.AttributeAmount")
            amount_location = ExpectedPointer(line, armor_ref)
            amount_raw_api_object.set_location(amount_location)

            attribute = dataset.pregen_nyan_objects["aux.attribute.types.Health"].get_nyan_object()
            amount_raw_api_object.add_raw_member("type",
                                                 attribute,
                                                 "engine.aux.attribute.AttributeAmount")
            amount_raw_api_object.add_raw_member("amount",
                                                 armor_amount,
                                                 "engine.aux.attribute.AttributeAmount")

            line.add_raw_api_object(amount_raw_api_object)
            # =================================================================================
            amount_expected_pointer = ExpectedPointer(line, amount_name)
            armor_raw_api_object.add_raw_member("block_value",
                                                amount_expected_pointer,
                                                resistance_parent)

            line.add_raw_api_object(armor_raw_api_object)
            armor_expected_pointer = ExpectedPointer(line, armor_ref)
            resistances.append(armor_expected_pointer)

        # TODO: Fallback type

        return resistances
