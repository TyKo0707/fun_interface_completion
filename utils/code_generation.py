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
    if not pd.isna(row.access_modifiers_annotation):
        for annotation in row.access_modifiers_annotation.split(', '):
            text += f"{annotation}\n"

    # Add test-annotations (if there are any) to text
    if not pd.isna(row.access_modifiers_test):
        for annotation in row.access_modifiers_test.split(', '):
            text += f"{annotation}\n"

    # Create signature for function (access modifiers, type identifier, formal parameters) and add it to text
    parameters = '' if pd.isna(row.formal_parameters) else row.formal_parameters
    signature = f"{row.access_modifiers.replace(', ', ' ')} {row.type_identifier} <extra_id_0>( {parameters} ) "
    text += signature

    # Add code block without comments to text
    if not pd.isna(row.block):
        # Remove comments
        code_block = re.sub(r'/\*.*?\*/', '', str(row.block), flags=re.DOTALL)
        code_block = re.sub(r'//.*?\n', '', code_block)
        text += code_block
    else:
        text += ';'

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
