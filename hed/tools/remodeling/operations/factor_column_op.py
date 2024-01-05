""" Create tabular file factor columns from column values. """

from hed.tools.remodeling.operations.base_op import BaseOp

# TODO: Does not handle empty factor names.
# TODO: Does not handle optional return columns.
# TODO: Same length factornames and factorvalues


class FactorColumnOp(BaseOp):
    """ Create tabular file factor columns from column values.

    Required remodeling parameters:   
        - **column_name** (*str*):  The name of a column in the DataFrame. 

    Optional remodeling parameters
        - **factor_names** (*list*):   Names to use as the factor columns.  
        - **factor_values** (*list*):  Values in the column column_name to create factors for.    

    """
    NAME = "factor_column"

    PARAMS = {
        "type": "object",
        "properties": {
            "column_name": {
                "type": "string"
            },
            "factor_names": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "minItems": 1,
                "uniqueItems": True
            },
            "factor_values": {
                "type": "array",
                "items": {
                        "type": "string"
                },
                "minItems": 1,
                "uniqueItems": True
            }
        },
        "required": [
            "column_name"
        ],
        "dependentRequired": {
            "factor_names": ["factor_values"]
        },
        "additionalProperties": False
    }

    def __init__(self, parameters):
        """ Constructor for the factor column operation.

        Parameters:
            parameters (dict): Parameter values for required and optional parameters.

        """
        super().__init__(self.PARAMS, parameters)
        self.column_name = parameters['column_name']
        self.factor_values = parameters['factor_values']
        self.factor_names = parameters['factor_names']
        if self.factor_names and len(self.factor_values) != len(self.factor_names):
            raise ValueError("FactorNamesLenBad",
                             f"The factor_names length {len(self.factor_names)} must be empty or equal" +
                             f"to the factor_values length {len(self.factor_values)} .")

    def do_op(self, dispatcher, df, name, sidecar=None):
        """ Create factor columns based on values in a specified column.

        Parameters:
            dispatcher (Dispatcher): Manages the operation I/O.
            df (DataFrame): The DataFrame to be remodeled.
            name (str): Unique identifier for the dataframe -- often the original file path.
            sidecar (Sidecar or file-like): Not needed for this operation.

        Returns:
            DataFrame: A new DataFrame with the factor columns appended.

        """

        factor_values = self.factor_values
        factor_names = self.factor_names
        if len(factor_values) == 0:
            factor_values = df[self.column_name].unique()
            factor_names = [self.column_name + '.' +
                            str(column_value) for column_value in factor_values]

        df_new = df.copy()
        for index, factor_value in enumerate(factor_values):
            factor_index = df_new[self.column_name].map(
                str).isin([str(factor_value)])
            column = factor_names[index]
            df_new[column] = factor_index.astype(int)
        return df_new

    @staticmethod
    def validate_input_data(parameters):
        if parameters.get("factor_names", False):
            if len(parameters.get("factor_names")) != len(parameters.get("factor_values")):
                return ["The list in factor_names, in the factor_column operation, should have the same number of items as factor_values."]
            else: 
                return []
        else:
            return []
