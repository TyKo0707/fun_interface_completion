import pandas as pd


def format_tuple(value: str) -> str:
    """
    Formats a tuple-like string into a readable format.

    Parameters:
    - value (str): The input string representing a tuple.

    Returns:
    - str: The formatted string.
    """
    param_list = value[1:-1].split(', ')
    if len(param_list) == 1:
        return param_list[0]
    elif len(param_list) == 0:
        return ''
    else:
        return ', '.join(param_list)


def format_cell(value: str) -> str:
    """
    Formats a cell value, converting lists to comma-separated strings.

    Parameters:
    - value (str): The input value to be formatted.

    Returns:
    - str: The formatted value.
    """
    if isinstance(value, list):
        return ', '.join(value)
    return value


def split_into_types(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits a DataFrame into different types of functions.

    Parameters:
    - df: The input DataFrame containing function information.

    Returns:
    - tuple: A tuple of DataFrames representing multiline functions, abstract functions, tests, and one-liners.
    """
    multiline_functions_df = df[(df.is_multiline == True) & (df.is_test == False)].reset_index(drop=True)
    abstract_functions_df = df[(df.is_abstract == True) & (df.is_test == False)].reset_index(drop=True)
    tests_df = df[df.is_test == True].reset_index(drop=True)
    one_liners_df = df[~df['function_id'].isin(multiline_functions_df['function_id']) &
                       ~df['function_id'].isin(abstract_functions_df['function_id']) &
                       ~df['function_id'].isin(tests_df['function_id'])].reset_index(drop=True)
    return multiline_functions_df, abstract_functions_df, tests_df, one_liners_df
