import unittest
import os

from hed.errors.error_types import ValidationErrors, ErrorContext
from tests.validator.test_tag_validator import TestValidatorBase


class TestHed3(TestValidatorBase):
    schema_file = "../data/HED8.0.0-alpha.3_add_currency.xml"


class IndividualHedTagsShort(TestHed3):
    @staticmethod
    def string_obj_func(validator):
        return validator._validate_individual_tags_in_hed_string

    def test_exist_in_schema(self):
        test_strings = {
            'takesValue': 'Duration/3 ms',
            'full': 'Animal-agent',
            'extensionsAllowed': 'Item/Beaver',
            'leafExtension': 'Experiment-procedure/Something',
            'nonExtensionsAllowed': 'Event/Nonsense',
            'invalidExtension': 'Attribute/Red',
            'invalidExtension2': 'Attribute/Red/Extension2',
            'usedToBeIllegalComma': 'Attribute/Informational/Label/This is a label,This/Is/A/Tag',
        }
        expected_results = {
            'takesValue': True,
            'full': True,
            'extensionsAllowed': True,
            'leafExtension': False,
            'nonExtensionsAllowed': False,
            'invalidExtension': False,
            'invalidExtension2': False,
            'usedToBeIllegalComma': False
        }
        expected_issues = {
            'takesValue': [],
            'full': [],
            'extensionsAllowed': [],
            'leafExtension': self.format_error_but_not_really(ValidationErrors.INVALID_EXTENSION, tag=0),
            'nonExtensionsAllowed': self.format_error_but_not_really(ValidationErrors.INVALID_EXTENSION, tag=0),
            'invalidExtension': self.format_error_but_not_really(ValidationErrors.INVALID_PARENT_NODE, tag=0, index_in_tag=10,
                                                                 index_in_tag_end=13,
                                                                 expected_parent_tag="Attribute/Sensory/Visual/Color/CSS-color/Red-color/Red"),
            'invalidExtension2': self.format_error_but_not_really(ValidationErrors.INVALID_PARENT_NODE, tag=0, index_in_tag=10,
                                                                  index_in_tag_end=13,
                                                                  expected_parent_tag="Attribute/Sensory/Visual/Color/CSS-color/Red-color/Red"),
            'usedToBeIllegalComma': self.format_error_but_not_really(ValidationErrors.NO_VALID_TAG_FOUND, tag=1,
                                                                     index_in_tag=0, index_in_tag_end=4),
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, False)

    def test_proper_capitalization(self):
        test_strings = {
            'proper': 'Event/Sensory-event',
            'camelCase': 'EvEnt/Something',
            'takesValue': 'Attribute/Temporal rate/20 Hz',
            'numeric': 'Repetition/20',
            'lowercase': 'Event/something'
        }
        expected_results = {
            'proper': True,
            'camelCase': True,
            'takesValue': True,
            'numeric': True,
            'lowercase': False
        }
        expected_issues = {
            'proper': [],
            'camelCase': [],
            'takesValue': [],
            'numeric': [],
            'lowercase': self.format_error_but_not_really(ValidationErrors.HED_STYLE_WARNING, tag=0)
        }
        self.validator_syntactic(test_strings, expected_results, expected_issues, True)

    def test_child_required(self):
        test_strings = {
            'hasChild': 'Experimental-stimulus',
            'missingChild': 'Label'
        }
        expected_results = {
            'hasChild': True,
            'missingChild': False
        }
        expected_issues = {
            'hasChild': [],
            'missingChild': self.format_error_but_not_really(ValidationErrors.HED_TAG_REQUIRES_CHILD, tag=0)
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, True)

    def test_required_units(self):
        test_strings = {
            'hasRequiredUnit': 'Duration/3 ms',
            'missingRequiredUnit': 'Duration/3',
            'notRequiredNoNumber': 'Color/Red',
            'notRequiredNumber': 'Color/Red/0.5',
            'notRequiredScientific': 'Color/Red/5.2e-1',
            'timeValue': 'Clock-face/08:30',
            # Update test - This one is currently marked as valid because clock face isn't in hed3
            'invalidTimeValue': 'Clock-face/8:30',
        }
        expected_results = {
            'hasRequiredUnit': True,
            'missingRequiredUnit': False,
            'notRequiredNoNumber': True,
            'notRequiredNumber': True,
            'notRequiredScientific': True,
            'timeValue': True,
            'invalidTimeValue': True,
        }
        legal_clock_time_units = ['hour:min', 'hour:min:sec']
        expected_issues = {
            'hasRequiredUnit': [],
            'missingRequiredUnit': self.format_error_but_not_really(ValidationErrors.HED_UNITS_MISSING, tag=0,
                                                                    default_unit='s'),
            'notRequiredNoNumber': [],
            'notRequiredNumber': [],
            'notRequiredScientific': [],
            'timeValue': [],
            'invalidTimeValue': [],
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, True)

    def test_correct_units(self):
        test_strings = {
            'correctUnit': 'Duration/3 ms',
            'correctUnitScientific': 'Duration/3.5e1 ms',
            'correctPluralUnit': 'Duration/3 milliseconds',
            'correctNoPluralUnit': 'Frequency/3 hertz',
            'correctNonSymbolCapitalizedUnit': 'Duration/3 MilliSeconds',
            'correctSymbolCapitalizedUnit': 'Frequency/3 kHz',
            'incorrectUnit': 'Duration/3 cm',
            'incorrectPluralUnit': 'Frequency/3 hertzs',
            'incorrectSymbolCapitalizedUnit': 'Frequency/3 hz',
            'incorrectSymbolCapitalizedUnitModifier': 'Frequency/3 KHz',
            'notRequiredNumber': 'Color/Red/0.5',
            'notRequiredScientific': 'Color/Red/5e-1',
            'specialAllowedCharBadUnit': 'Creation-date/bad_date',
            'specialAllowedCharUnit': 'Creation-date/1900-01-01T01:01:01',
            'specialAllowedCharCurrency': 'Event/Currency-Test/$100',
            'specialNotAllowedCharCurrency': 'Event/Currency-Test/@100'
            # Update tests - 8.0 currently has no clockTime nodes.
            # 'properTime': 'Item/2D shape/Clock face/08:30',
            # 'invalidTime': 'Item/2D shape/Clock face/54:54'
        }
        expected_results = {
            'correctUnit': True,
            'correctUnitScientific': True,
            'correctPluralUnit': True,
            'correctNoPluralUnit': True,
            'correctNonSymbolCapitalizedUnit': True,
            'correctSymbolCapitalizedUnit': True,
            'incorrectUnit': False,
            'incorrectPluralUnit': False,
            'incorrectSymbolCapitalizedUnit': False,
            'incorrectSymbolCapitalizedUnitModifier': False,
            'notRequiredNumber': True,
            'notRequiredScientific': True,
            'specialAllowedCharBadUnit': False,
            'specialAllowedCharUnit': True,
            'properTime': True,
            'invalidTime': True,
            'specialAllowedCharCurrency': True,
            'specialNotAllowedCharCurrency': False,
        }
        legal_time_units = ['s', 'second', 'day', 'minute', 'hour']
        legal_clock_time_units = ['hour:min', 'hour:min:sec']
        legal_datetime_units = ['YYYY-MM-DDThh:mm:ss']
        legal_freq_units = ['Hz', 'hertz']
        legal_currency_units = ['dollar', "$", "point"]

        expected_issues = {
            'correctUnit': [],
            'correctUnitScientific': [],
            'correctPluralUnit': [],
            'correctNoPluralUnit': [],
            'correctNonSymbolCapitalizedUnit': [],
            'correctSymbolCapitalizedUnit': [],
            'incorrectUnit': self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,
                                                              tag=0, unit_class_units=legal_time_units),
            'incorrectPluralUnit': self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,
                                                                    tag=0, unit_class_units=legal_freq_units),
            'incorrectSymbolCapitalizedUnit': self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,
                                                                               tag=0,
                                                                               unit_class_units=legal_freq_units),
            'incorrectSymbolCapitalizedUnitModifier': self.format_error_but_not_really(
                ValidationErrors.HED_UNITS_INVALID, tag=0, unit_class_units=legal_freq_units),
            'notRequiredNumber': [],
            'notRequiredScientific': [],
            'specialAllowedCharBadUnit':  self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,
                                                                           tag=0, unit_class_units=legal_datetime_units),
            'specialAllowedCharUnit': [],
            # 'properTime': [],
            # 'invalidTime': self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,  tag=0,
            #                                 unit_class_units=legal_clock_time_units)
            'specialAllowedCharCurrency': [],
            'specialNotAllowedCharCurrency': self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,
                                                                               tag=0,
                                                                               unit_class_units=legal_currency_units),
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, True)

    def test_extensions(self):
        test_strings = {
            'invalidExtension': 'Experiment-control/Animal-agent',
        }
        expected_results = {
            'invalidExtension': False,
        }
        expected_issues = {
            'invalidExtension': self.format_error_but_not_really(ValidationErrors.INVALID_PARENT_NODE, tag=0,
                                                                 index_in_tag=19, index_in_tag_end=31,
                                                                 expected_parent_tag="Agent/Animal-agent"),
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, False)

    def test_invalid_placeholder_in_normal_string(self):
        test_strings = {
            'invalidPlaceholder': 'Duration/# ms',
        }
        expected_results = {
            'invalidPlaceholder': False,
        }
        expected_issues = {
            'invalidPlaceholder': self.format_error_but_not_really(ValidationErrors.INVALID_TAG_CHARACTER,
                                                                   tag=0,
                                                                   index_in_tag=9, index_in_tag_end=10,
                                                                   actual_error=ValidationErrors.HED_VALUE_INVALID),
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, False)

    def test_span_reporting(self):
        test_strings = {
            'orgTagDifferent': 'Duration/23 hz',
            'orgTagDifferent2': 'Duration/23 hz, Duration/23 hz',
        }
        expected_results = {
            'orgTagDifferent': False,
            'orgTagDifferent2': False,
        }
        tag_unit_class_units = ['day', 'hour', 'minute', 's', 'second']
        expected_issues = {
            'orgTagDifferent': self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,
                                                                tag=0,
                                                                unit_class_units=tag_unit_class_units),
            'orgTagDifferent2': self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,
                                                                 tag=0,
                                                                 unit_class_units=tag_unit_class_units)
                                + self.format_error_but_not_really(ValidationErrors.HED_UNITS_INVALID,
                                                                   tag=1,
                                                                   unit_class_units=tag_unit_class_units),
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, False)


class TestTagLevels3(TestHed3):
    @staticmethod
    def string_obj_func(validator):
        return validator._validate_groups_in_hed_string

    def test_no_duplicates(self):
        test_strings = {
            'topLevelDuplicate': 'Event/Sensory-event,Event/Sensory-event',
            'groupDuplicate': 'Item/Object/Man-made-object/VehicleTrain,(Event/Sensory-event,'
                              'Attribute/Sensory/Visual/Color/CSS-color/Purple-color/Purple,Event/Sensory-event)',
            'noDuplicate': 'Event/Sensory-event,'
                           'Item/Object/Man-made-object/VehicleTrain,'
                           'Attribute/Sensory/Visual/Color/CSS-color/Purple-color/Purple',
            'legalDuplicate': 'Item/Object/Man-made-object/VehicleTrain,(Item/Object/Man-made-object/VehicleTrain,'
                              'Event/Sensory-event)',
        }
        expected_results = {
            'topLevelDuplicate': False,
            'groupDuplicate': False,
            'legalDuplicate': True,
            'noDuplicate': True
        }
        expected_issues = {
            'topLevelDuplicate': self.format_error_but_not_really(ValidationErrors.HED_TAG_REPEATED,
                                                                  tag=1),
            'groupDuplicate': self.format_error_but_not_really(ValidationErrors.HED_TAG_REPEATED,
                                                               tag=3),
            'legalDuplicate': [],
            'noDuplicate': []
        }
        self.validator_syntactic(test_strings, expected_results, expected_issues, False)

    def test_no_duplicates_semantic(self):
        test_strings = {
            'mixedLevelDuplicates': 'Man-made-object/Vehicle/Boat, Vehicle/Boat',
            'mixedLevelDuplicates2': 'Man-made-object/Vehicle/Boat, Boat'
        }
        expected_results = {
            'mixedLevelDuplicates': False,
            'mixedLevelDuplicates2': False,
        }
        expected_issues = {
            'mixedLevelDuplicates': self.format_error_but_not_really(ValidationErrors.HED_TAG_REPEATED,
                                                                     tag=1),
            'mixedLevelDuplicates2': self.format_error_but_not_really(ValidationErrors.HED_TAG_REPEATED,
                                                                      tag=1),
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, False)

    def test_topLevelTagGroup_validation(self):
        test_strings = {
            'invalid1': 'Definition/InvalidDef',
            'valid1': '(Definition/ValidDef)',
            'valid2': '(Definition/ValidDef), (Definition/ValidDef2)',
            'invalid2': '(Event, (Definition/InvalidDef2))',
            'invalidTwoInOne': '(Definition/InvalidDef2, Definition/InvalidDef3)',
            'invalid2TwoInOne': '(Definition/InvalidDef2, Onset)',
        }
        expected_results = {
            'invalid1': False,
            'valid1': True,
            'valid2': True,
            'invalid2': False,
            'invalidTwoInOne': False,
            'invalid2TwoInOne': False,
        }
        expected_issues = {
            'invalid1': self.format_error_but_not_really(ValidationErrors.HED_TOP_LEVEL_TAG,
                                                         tag=0),
            'valid1': [],
            'valid2': [],
            'invalid2': self.format_error_but_not_really(ValidationErrors.HED_TOP_LEVEL_TAG,
                                                         tag=1),
            'invalidTwoInOne': self.format_error_but_not_really(ValidationErrors.HED_MULTIPLE_TOP_TAGS,
                                                                tag=0,
                                                                multiple_tags="Attribute/Informational/Definition/InvalidDef3".split(", ")),
            'invalid2TwoInOne': self.format_error_but_not_really(ValidationErrors.HED_MULTIPLE_TOP_TAGS,
                                                                 tag=0,
                                                                 multiple_tags="Data-property/Spatiotemporal-property/Temporal-property/Onset".split(", ")),
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, False)

    def test_taggroup_validation(self):
        test_strings = {
            'invalid1': 'Def-Expand/InvalidDef',
            'invalid2': 'Def-Expand/InvalidDef, Event, (Event)',
            'invalid3': 'Event, (Event), Def-Expand/InvalidDef',
            'valid1': '(Def-Expand/ValidDef)',
            'valid2': '(Def-Expand/ValidDef), (Def-Expand/ValidDef2)',
            'valid3': '(Event, (Def-Expand/InvalidDef2))',
            # This case should possibly be flagged as invalid
            'semivalid1': '(Def-Expand/InvalidDef2, Def-Expand/InvalidDef3)',
            'semivalid2': '(Def-Expand/InvalidDef2, Onset)',
        }
        expected_results = {
            'invalid1': False,
            'invalid2': False,
            'invalid3': False,
            'valid1': True,
            'valid2': True,
            'valid3': True,
            'semivalid1': True,
            'semivalid2': True,
        }
        expected_issues = {
            'invalid1': self.format_error_but_not_really(ValidationErrors.HED_TAG_GROUP_TAG,
                                                         tag=0),
            'invalid2': self.format_error_but_not_really(ValidationErrors.HED_TAG_GROUP_TAG,
                                                         tag=0),
            'invalid3': self.format_error_but_not_really(ValidationErrors.HED_TAG_GROUP_TAG,
                                                         tag=2),
            'valid1': [],
            'valid2': [],
            'valid3': [],
            'semivalid1': [],
            'semivalid2': []
        }
        self.validator_semantic(test_strings, expected_results, expected_issues, False)


if __name__ == '__main__':
    unittest.main()
