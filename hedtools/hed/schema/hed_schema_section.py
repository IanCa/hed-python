from hed.schema.hed_schema_constants import HedSectionKey


class HedSchemaEntry:
    def __init__(self, long_name, section):
        self.long_name = long_name
        # key: property/attribute name, value = property value.  Will often be a bool
        self.attributes = {}
        self.description = None
        self.value = None
        self._section = section
        
        # This section is largely unused
        self._unknown_attributes = None

    def set_attribute_value(self, attribute_name, attribute_value, skip_validation=False):
        if not attribute_value:
            return

        if not skip_validation and attribute_name not in self._section.valid_attributes:
            #raise ValueError("This is an unknown value")
            print(f"Unknown attribute {attribute_name}")
            if self._unknown_attributes is None:
                self._unknown_attributes = {}
            self._unknown_attributes[attribute_name] = attribute_value
        self.attributes[attribute_name] = attribute_value

    def has_attribute(self, attribute_name, return_value=False):
        if return_value:
            return self.attributes.get(attribute_name, None)
        else:
            return attribute_name in self.attributes

    def __eq__(self, other):
        if self.long_name != other.long_name:
            return False
        if self.attributes != other.attributes:
            # We only want to compare known attributes
            self_attr = {key: value for key, value in self.attributes.items() if not self._unknown_attributes or key not in self._unknown_attributes}
            other_attr = {key: value for key, value in other.attributes.items() if not other._unknown_attributes or key not in other._unknown_attributes}
            if self_attr != other_attr:
                return False
        if self.description != other.description:
            return False
        if self.value != other.value:
            return False
        return True


class HedSchemaSection():
    def __init__(self, section_key):
        # {lower_case_name: HedSchemaEntry}
        self.all_names = {}
        self._section_key = section_key
        self.case_sensitive = False

        # Points to the entries in attributes
        self.valid_attributes = {}

    def __eq__(self, other):
        if self.all_names != other.all_names:
            return False
        if self._section_key != other._section_key:
            return False
        if self.case_sensitive != other.case_sensitive:
            return False
        return True

    def _add_to_dict(self, name):
        name_key = name
        if self._section_key == HedSectionKey.AllTags:
            name_key = name.lower()

        self.all_names[name_key] = HedSchemaEntry(name, self)
