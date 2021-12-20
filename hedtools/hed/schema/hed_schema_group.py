"""
"""

# todo: Switch various properties to this once we require python 3.8

from hed.errors.exceptions import HedExceptions, HedFileError


class HedSchemaGroup:
    """
        This class handles combining multiple HedSchema objects for validation.

        You cannot save/load/etc the combined schema object directly.
    """
    def __init__(self, schema_list):
        """
        Create combination of multiple HedSchema objects you can use with the validator.

        Note: will raise HedFileError if two schemas share the same name_prefix

        Parameters
        ----------
        Returns
        -------
        HedSchemaGroup
            A HedSchemaCombined object.
        """
        library_prefixes = [hed_schema._library_prefix for hed_schema in schema_list]
        if len(set(library_prefixes)) != len(library_prefixes):
            raise HedFileError(HedExceptions.SCHEMA_DUPLICATE_PREFIX,
                               "Multiple schemas share the same tag name_prefix.  This is not allowed.",
                               filename="Combined Schema")
        self._schemas = {hed_schema._library_prefix: hed_schema for hed_schema in schema_list}

    # ===============================================
    # General schema properties/functions
    # ===============================================
    @property
    def has_duplicate_tags(self):
        """
        Returns True if this is a valid hed3 schema with no duplicate short tags.

        Returns
        -------
        bool
            Returns True if this is a valid hed3 schema with no duplicate short tags.
        """
        return any([schema.has_duplicate_tags for schema in self._schemas.values()])

    @property
    def unit_classes(self):
        return all([schema.unit_classes for schema in self._schemas.values()])

    @property
    def is_hed3_compatible(self):
        return all([schema.is_hed3_compatible for schema in self._schemas.values()])

    @property
    def is_hed3_schema(self):
        # All combined schemas are implicitly hed3.
        return True

    @property
    def unit_modifiers(self):
        return all([schema.unit_modifiers for schema in self._schemas.values()])

    @property
    def value_classes(self):
        return all([schema.value_classes for schema in self._schemas.values()])

    def __eq__(self, other):
        return self._schemas == other._schemas

    def schema_for_prefix(self, prefix):
        """
            Return the specific HedSchema object for the given tag name_prefix.

            Returns None if name_prefix is invalid.

        Parameters
        ----------
        prefix : str
            A schema library name_prefix to get the schema for.

        Returns
        -------
        schema: HedSchema
            The specific schema for this library name_prefix
        """
        schema = self._schemas.get(prefix)
        return schema

    @property
    def valid_prefixes(self):
        """
            Gets a list of all prefixes this schema will accept.

        Returns
        -------
        valid_prefixes: [str]
            A list of valid tag prefixes for this schema.
        """
        return list(self._schemas.keys())

    def check_compliance(self, also_check_for_warnings=True, name=None,
                         error_handler=None):
        """
            Checks for hed3 compliance of this schema.

        Parameters
        ----------
        also_check_for_warnings : bool, default True
            If True, also checks for formatting issues like invalid characters, capitalization, etc.
        name: str
            If present, will use this as the filename for context, rather than using the actual filename
            Useful for temp filenames.
        error_handler : ErrorHandler or None
            Used to report errors.  Uses a default one if none passed in.
        Returns
        -------
        issue_list : [{}]
            A list of all warnings and errors found in the file.
        """
        issues_list = []
        for schema in self._schemas.values():
            issues_list += schema.check_compliance(also_check_for_warnings, name, error_handler)
        return issues_list

    # ===============================================
    # Basic tag attributes
    # ===============================================

    # ===============================================
    # More complex tag attributes/combinations of tags etc.
    # ===============================================
    def get_unit_class_default_unit(self, original_tag):
        """Gets the default unit class unit that is associated with the specified tag.

        Parameters
        ----------
        original_tag: HedTag
            The tag that is used to do the validation.
        Returns
        -------
        str
            The default unit class unit associated with the specific tag. If the tag doesn't have a unit class then an
            empty string is returned.

        """
        schema = self._schemas.get(original_tag.library_prefix)
        if schema:
            return schema.get_unit_class_default_unit(original_tag)

    def get_tag_unit_class_units(self, original_tag):
        """Gets the unit class units associated with a particular tag.

        Parameters
        ----------
        original_tag: HedTag
            The tag that is used to do the validation.
        Returns
        -------
        []
            A list containing the unit class units associated with a particular tag. A empty list will be returned if
            the tag doesn't have unit class units associated with it.

        """
        schema = self._schemas.get(original_tag.library_prefix)
        if schema:
            return schema.get_tag_unit_class_units(original_tag)

    def get_all_tags_with_attribute(self, key):
        all_tags = set()
        for schema in self._schemas.values():
            all_tags.update(schema.get_all_tags_with_attribute(key))
        return all_tags
