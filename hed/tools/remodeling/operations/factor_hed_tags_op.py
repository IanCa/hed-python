""" Append columns of factors based on column values to a columnar file. """


import pandas as pd
import numpy as np
from hed.tools.remodeling.operations.base_op import BaseOp
from hed.models.tabular_input import TabularInput
from hed.models.sidecar import Sidecar
from hed.models.df_util import get_assembled
from hed.tools.analysis.analysis_util import get_expression_parsers, search_strings
from hed.tools.analysis.event_manager import EventManager
from hed.tools.analysis.hed_tag_manager import HedTagManager


class FactorHedTagsOp(BaseOp):
    """ Append columns of factors based on column values to a columnar file.

    Required remodeling parameters:   
        - **queries** (*list*): Queries to be applied successively as filters.       

    Optional remodeling parameters:   
        - **expand_context** (*bool*): Expand the context if True.
        - **query_names** (*list*):  Column names for the query factors. 
        - **remove_types** (*list*):  Structural HED tags to be removed (such as Condition-variable or Task).
        - **expand_context** (*bool*): If true, expand the context based on Onset, Offset, and Duration.

    Notes:  
        - If query names are not provided, *query1*, *query2*, ... are used.   
        - When the context is expanded, the effect of events for temporal extent is accounted for.

    """
    NAME = "factor_hed_tags"
    
    PARAMS = {
        "type": "object",
        "properties": {
            "queries": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "minItems": 1,
                "uniqueItems": True
            },
            "query_names": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "minItems": 1,
                "uniqueItems": True
            },
            "remove_types": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "minItems": 1,
                "uniqueItems": True
            },
            "expand_context": {
                "type": "boolean"
            },
            "replace_defs": {
                "type": "boolean"
            }
        },
        "required": [
            "queries"
        ],
        "additionalProperties": False
    }

    def __init__(self, parameters):
        """ Constructor for the factor HED tags operation.

        Parameters:
            parameters (dict):  Actual values of the parameters for the operation.

        """
        super().__init__(parameters)
        self.queries = parameters['queries']
        self.remove_types = parameters.get('remove_types', [])
        self.expand_context = parameters.get('expand_context', True)
        self.replace_defs = parameters.get('replace_defs', True)
        self.expression_parsers, self.query_names = get_expression_parsers(self.queries,
                                                                           parameters.get('query_names', None))

    def do_op(self, dispatcher, df, name, sidecar=None):
        """ Factor the column using HED tag queries.

        Parameters:
            dispatcher (Dispatcher): Manages the operation I/O.
            df (DataFrame): The DataFrame to be remodeled.
            name (str): Unique identifier for the dataframe -- often the original file path.
            sidecar (Sidecar or file-like):  Only needed for HED operations.

        Returns:
            Dataframe: A new dataframe after processing.

        :raises ValueError:
            - If a name for a new query factor column is already a column.

        """

        if sidecar and not isinstance(sidecar, Sidecar):
            sidecar = Sidecar(sidecar)
        input_data = TabularInput(df.copy().fillna('n/a'), sidecar=sidecar, name=name)
        column_names = list(df.columns)
        for query_name in self.query_names:
            if query_name in column_names:
                raise ValueError("QueryNameAlreadyColumn",
                                 f"Query [{query_name}]: is already a column name of the data frame")
        df_list = [input_data.dataframe]
        tag_man = HedTagManager(EventManager(input_data, dispatcher.hed_schema),
                                remove_types=self.remove_types)
        hed_objs = tag_man.get_hed_objs(include_context=self.expand_context, replace_defs=self.replace_defs)
        df_factors = search_strings(hed_objs, self.expression_parsers, query_names=self.query_names)
        if len(df_factors.columns) > 0:
            df_list.append(df_factors)
        df_new = pd.concat(df_list, axis=1)
        df_new.replace('n/a', np.nan, inplace=True)
        return df_new

    @staticmethod
    def validate_input_data(parameters):
        queries = parameters.get("queries", None)
        names = parameters.get("query_names", None)
        if names and queries and (len(names) != len(parameters["queries"])):
            return ["factor_hed_tags_op: query_names must be same length as queries."]
        return []
