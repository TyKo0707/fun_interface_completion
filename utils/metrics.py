import spacy
import numpy as np
import warnings

warnings.filterwarnings("ignore", message=r"\[W008\]", category=UserWarning)

# spacy.cli.download("en_core_web_lg")
nlp = spacy.load("en_core_web_lg")


def code_gen_f1_score_and_accuracy(predictions: list[str], references: list[str]) -> tuple:
    """
    Calculates precision, recall, F1 score, and accuracy for a set of predictions and references.

    Parameters:
    - predictions (list): A list of predicted values.
    - references (list): A list of reference values.

    Returns:
    - tuple: A tuple containing precision, recall, F1 score, and accuracy.
    """
    if len(predictions) == 0 or len(references) == 0:
        return 0, 0, 0, 0

    TP = np.sum(np.isin(references, predictions))
    FP = len(predictions) - TP
    FN = len(references) - TP

    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0

    accuracy = TP / len(references)

    return precision, recall, f1_score, accuracy


def code_gen_name_similarity(predictions: list[str], references: list[str]) -> float:
    """
    Calculates the similarity between a set of predictions and references.

    Parameters:
    - predictions (list): A list of predicted values.
    - references (list): A list of reference values.

    Returns:
    - float: The similarity between the predictions and references.
    """
    if len(predictions) == 0 or len(references) == 0:
        return 0
    predictions = ' '.join(predictions)
    references = ' '.join(references)

    doc1 = nlp(predictions)
    doc2 = nlp(references)

    return doc1.similarity(doc2)
