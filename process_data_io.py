import pandas as pd
from tqdm import tqdm
from utils.code_generation import format_text_for_code_gen
from environs import Env

env = Env()
env.read_env()
UNPROCESSED_FUNCTIONS_DATASET = env.str("UNPROCESSED_FUNCTIONS_DATASET")
MAIN_DATASET = env.str("MAIN_DATASET")


def categorize_length(signature):
    length = len(signature)
    if length <= 23:
        return '0-20'
    elif length <= 43:
        return '20-50'
    elif length <= 73:
        return '50-100'
    else:
        return '100+'


def extract_input_output_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts input and output data for code generation from a DataFrame and constructs a new DataFrame.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing function information.

    Returns:
    - pd.DataFrame: A new DataFrame containing columns for function_id, input, label, is_multiline, is_test, and is_abstract.
    """
    inputs = []

    for index in tqdm(range(df.shape[0])):
        row = df.iloc[index]
        row_input = format_text_for_code_gen(row)
        inputs.append(row_input)

    return pd.DataFrame({'function_id': df.function_id, 'signature': inputs, 'body': df.function_body,
                         'is_single_expression': df.is_single_expression, 'is_test': df.is_test})


if __name__ == '__main__':
    functions_df = pd.read_csv(UNPROCESSED_FUNCTIONS_DATASET, index_col=0).sample(frac=1).reset_index(drop=True)
    processed_io_df = extract_input_output_from_df(functions_df)

    # Categorize the length of the signature strings
    processed_io_df['length_category'] = processed_io_df['signature'].apply(categorize_length)
    dummies = pd.get_dummies(processed_io_df['length_category'])
    processed_io_df = pd.concat([processed_io_df, dummies], axis=1)
    processed_io_df.drop('length_category', axis=1, inplace=True)

    processed_io_df.to_parquet(MAIN_DATASET, engine='fastparquet', compression='gzip', index=False)
