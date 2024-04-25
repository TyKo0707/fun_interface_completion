import tree_sitter
import os
from environs import Env
from tqdm import tqdm

from utils.process_dataframe import format_tuple, format_cell
import pandas as pd

env = Env()
env.read_env()
LANGUAGE_BUILDER_PATH = env.str("LANGUAGE_BUILDER_PATH")
KOTLIN_FILES_DIRECTORY = env.str("KOTLIN_FILES_DIRECTORY")
UNPROCESSED_FUNCTIONS_DATASET = env.str("UNPROCESSED_FUNCTIONS_DATASET")
TEST_PATH = env.str("TEST_PATH")

functions = {'simple_identifier': [], 'function_value_parameters': [], 'user_type': [],
             'modifiers': [], 'function_body': [], 'type_parameters': [], 'flags': []}


def extract_methods(node: tree_sitter.Node, empty_func=False):
    """
    Recursively traverses a syntax tree to extract information about method declarations.

    Parameters:
    - node (tree_sitter.Node): The root node of the syntax tree.

    The function recursively traverses the syntax tree and extracts information about method declarations,
    including identifiers, formal parameters, type identifiers, access modifiers, and code blocks.

    Does not return anything, but updates the global variable 'functions'.
    """

    # Skip abstract classes
    if node.type == 'class_declaration':
        for child in node.children:
            if 'modifier' in child.type or 'modifiers' in child.type:
                if 'abstract' in [ch.text.decode('utf8') for ch in child.children]:
                    return

    def add_flags(func_dict):
        if func_dict['function_body'][0].strip().startswith('='):
            func_dict['flags'].append('is_single_expression')
        if 'test' in func_dict['simple_identifier'][0].lower() or '@Test' in func_dict['modifiers']:
            func_dict['flags'].append('is_test')

    if node.type == 'function_declaration':
        children = node.children
        curr_function = {'simple_identifier': [], 'function_value_parameters': [], 'user_type': [],
                         'modifiers': [], 'function_body': [], 'type_parameters': [], 'flags': []}
        for child in children:
            if child.type == 'modifiers' or child.type == 'modifier':
                curr_function['modifiers'] = [mod.text.decode('utf8') for mod in child.children]
            elif child.type in ['function_body', 'function_value_parameters', 'simple_identifier', 'user_type',
                                'type_parameters']:
                curr_function[child.type].append(child.text.decode('utf8'))
                continue

        # Check if function is not empty
        if (curr_function['function_body'][0] == ('' or '{}')) and not empty_func:
            return
        else:
            add_flags(curr_function)
            for key in curr_function.keys():
                functions[key].append(curr_function[key])

    for child in node.children:
        extract_methods(child, empty_func)


def read_file(file_path: str) -> str:
    """
    Reads a file and returns its contents as a string.

    Parameters:
    - file_path (str): The path to the file to be read.

    Returns:
    - file_body (str): The contents of the file as a string.
    """
    encodings_to_try = ['utf-8', 'ISO-8859-1', 'windows-1252', 'utf-16']

    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                file_body = file.read()
            break
        except UnicodeDecodeError:
            continue
    return file_body


def extract_functions_from_file(file_path: str, empty_func=False):
    """
    Extracts functions from a file and updates the global variable 'functions'.

    Parameters:
    - file_path (str): The path to the file to be read.
    """
    code = read_file(file_path)
    try:
        tree = parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        extract_methods(root_node, empty_func)
    except:
        pass


def find_kotlin_files(global_repository_directory: str) -> list[str]:
    """
    Finds all Kotlin files in a directory and its subdirectories.

    Parameters:
    - global_repository_directory (str): The path to the directory to be searched.

    Returns:
    - res (list[str]): A list of paths to Kotlin files.
    """
    res = []
    for (dir_path, dir_names, file_names) in os.walk(global_repository_directory):
        res.extend([os.path.join(dir_path, file_name) for file_name in file_names if
                    file_name.endswith(".kt") or file_name.endswith(".kts")])
    return res


def test_extraction(data_path, golden_path, save_path):
    golden_df = pd.read_csv(golden_path)
    golden_df.drop(columns=['Unnamed: 0'], inplace=True)
    golden_df.fillna('', inplace=True)
    extract_functions_from_file(data_path, True)
    extract_functions_from_file(data_path, False)

    df_test = pd.DataFrame(functions)
    # Create strings from lists
    df_test = df_test.map(format_cell)
    # Format parameters column
    df_test['function_value_parameters'] = df_test['function_value_parameters'].apply(lambda x: format_tuple(x))
    df_test['function_value_parameters'] = df_test['function_value_parameters'] \
        .str.replace(r'\s+', ' ', regex=True).str.strip()

    # Empty functions dataset
    for key in functions: functions[key] = []

    if golden_df.equals(df_test):
        print('Test passed')
        df_test.to_csv(save_path)
        print(f'Your result was saved to {save_path}')
    else:
        print('Test failed')


if __name__ == "__main__":
    tree_sitter.Language.build_library(LANGUAGE_BUILDER_PATH, ['tree-sitter-kotlin'])
    KOTLIN_LANGUAGE = tree_sitter.Language(LANGUAGE_BUILDER_PATH, 'kotlin')
    parser = tree_sitter.Parser()
    parser.set_language(KOTLIN_LANGUAGE)

    kotlin_files = find_kotlin_files(KOTLIN_FILES_DIRECTORY)

    extract_test_path = TEST_PATH + 'extraction/'

    # Test extraction on different functions
    test_extraction(*[extract_test_path + path for path in
                      ['extraction_test.kt', 'extraction_test_gold.csv', 'extraction_test_res.csv']])

    for i in tqdm(range(len(kotlin_files))):
        extract_functions_from_file(kotlin_files[i])

    df = pd.DataFrame(functions)

    # Create strings from lists
    df = df.map(format_cell)

    # Format parameters column
    df['function_value_parameters'] = df['function_value_parameters'].apply(lambda x: format_tuple(x))
    df['function_value_parameters'] = df['function_value_parameters'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Create dummy columns from column flags
    df['is_single_expression'] = df['flags'].apply(lambda x: 'is_single_expression' in x.split(', '))
    df['is_test'] = df['flags'].apply(lambda x: 'is_test' in x.split(', '))
    df.drop(columns=['flags'], inplace=True)

    df = df.reset_index(drop=False)
    df = df.rename(columns={'index': 'function_id'})

    # Simple EDA
    df_size = len(df)
    count_is_single_expression = df['is_single_expression'].sum()
    count_is_test = df['is_test'].sum()
    count_both_false = len(df) - count_is_single_expression - count_is_test
    print(f"Occurrences of is_single_expression: {round(count_is_single_expression * 100 / df_size, 2)}%")
    print(f"Occurrences of is_test: {round(count_is_test * 100 / df_size, 2)}%")
    print(f"Occurrences of both false: {round(count_both_false * 100 / df_size, 2)}%")
    print(f'Size of a dataset (num. of methods): {df_size}')

    # Occurrences of is_single_expression: 36.32%
    # Occurrences of is_test: 16.35%
    # Occurrences of both false: 47.33%
    # Size of a dataset (num. of methods): 127661
    df.to_csv(UNPROCESSED_FUNCTIONS_DATASET, index=True)