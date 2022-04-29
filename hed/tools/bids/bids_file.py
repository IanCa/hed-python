import os
from hed.util.io_util import parse_bids_filename


class BidsFile:
    """ Represents the entity dictionary and file names for a BIDs file.

    Args:
        file_path (str):   Full path of the file.

    Attributes:
        file_path (str):     Real path of the file.
        suffix (str):        Suffix part of the filename.
        ext (str):           Extension (including the .).
        entity_dict (dict):  Dictionary of entity-names (keys) and entity-values (values).

    """

    def __init__(self, file_path):
        self.file_path = os.path.realpath(file_path)
        suffix, ext, entity_dict = parse_bids_filename(self.file_path)
        self.suffix = suffix
        self.ext = ext
        self.entity_dict = entity_dict

    def __str__(self):
        return self.file_path + ":\n\tname_suffix=" + self.suffix + " ext=" + self.ext + \
               " entity_dict=" + str(self.entity_dict)

