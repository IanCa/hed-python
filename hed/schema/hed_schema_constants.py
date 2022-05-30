
class HedSectionKey:
    """ Kegs designating specific sections in a HedSchema object.
    """
    # overarching category listing all tags
    AllTags = 'tags'
    # Overarching category listing all unit classes
    UnitClasses = 'unitClasses'
    # Overarching category listing all units(not divided by type)
    Units = 'units'
    # Overarching category listing all unit modifiers.
    UnitModifiers = 'unitModifiers'
    # Overarching category listing all value classes
    ValueClasses = "valueClasses"
    # These are the allowed attributes list, gathered from the schema on load.
    Attributes = 'attributes'
    # These are the allowed attribute property list, gathered from the schema on load.
    Properties = 'properties'


class HedKey:
    """ Known property and attribute names.

    Notes:
        - These names should match the attribute values in the XML/wiki.

    """
    # Tag attributes
    ExtensionAllowed = 'extensionAllowed'
    Recommended = 'recommended'
    Required = 'required'
    RequireChild = 'requireChild'
    TagGroup = 'tagGroup'
    TakesValue = 'takesValue'
    TopLevelTagGroup = 'topLevelTagGroup'
    Unique = 'unique'
    UnitClass = 'unitClass'
    ValueClass = "valueClass"
    RelatedTag = "relatedTag"
    SuggestedTag = "suggestedTag"

    # All known properties
    BoolProperty = 'boolProperty'
    UnitClassProperty = 'unitClassProperty'
    UnitProperty = 'unitProperty'
    UnitModifierProperty = 'unitModifierProperty'
    ValueClassProperty = 'valueClassProperty'

    SIUnit = 'SIUnit'
    UnitSymbol = 'unitSymbol'
    # Default Units for Type
    DefaultUnits = 'defaultUnits'
    UnitPrefix = 'unitPrefix'

    SIUnitModifier = 'SIUnitModifier'
    SIUnitSymbolModifier = 'SIUnitSymbolModifier'

    # value class attributes
    AllowedCharacter = 'allowedCharacter'


VERSION_ATTRIBUTE = 'version'
