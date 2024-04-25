import re

import pandas as pd


def format_text_for_code_gen(row: pd.Series) -> str:
    """
    Combines features from row in the method in a form of a text.

    Parameters:
    - row (pd.Series): A Pandas Series containing information about the method to be generated.

    Returns:
    - str: The formatted text for method.
    """
    text = ''

    # Add annotations to text
    if not pd.isna(row.modifiers):
        for annotation in row.modifiers.split(', '):
            if annotation.startswith('@'):
                text += f"{annotation}\n"
            else:
                text += f"{annotation} "

    # Different cases:
    # - user_type = ''
    # - user_type = IdeaSyncDetector, where we write it after the signature: fun (...): IdeaSyncDetector
    # - user_type = Iterable<V>, List<R>, where we must set first element before function name
    #   and second one as in the previous example: fun <V, R> Iterable<V>.funcName(...): List<R>
    user_type = ''
    if not pd.isna(row.user_type):
        if len(row.user_type.split('>,')) > 1:
            user_types = re.split(r",\s*(?![^<>]*>)", row.user_type)
            try:
                func_type, user_type = user_types[0], user_types[1]
                row.simple_identifier = f'{func_type}.{row.simple_identifier}'
            except:
                user_type = user_types[0]
        else:
            user_type = row.user_type

    # Create signature for function (access modifiers, type identifier, formal parameters) and add it to text
    parameters = '' if pd.isna(row.function_value_parameters) else row.function_value_parameters
    type_parameters = '' if pd.isna(row.type_parameters) else row.type_parameters + ' '
    signature = 'fun ' + type_parameters + f'{row.simple_identifier}({parameters})'
    text += signature
    if user_type != '':
        text += f': {user_type}'

    if row.is_single_expression:
        text += ' +'

    return text


def extract_tokens_from_camel(text: str, is_lower: bool = True) -> list[str] | str:
    """
    Extracts tokens from a camelCase or snake_case string.

    Parameters:
    - text (str): The input string to extract tokens from.
    - is_lower (bool, optional): A flag indicating whether to convert tokens to lowercase. Default is True.

    Returns:
    - list: A list of extracted tokens.
    """
    try:
        if len(text.split('_')) > 1:
            return text.split('_')
        else:
            return [i.lower() if is_lower else i for i in re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', text)]
    except:
        return ''
