import json


def load_dataset(data_path):
    """
    Load dataset from a JSONL file.

    Args:
        data_path (str): Path to the JSONL file.

    Returns:
        list: List of dictionaries, each containing a conversation.
    """
    dataset = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            dataset.append(json.loads(line))
    return dataset
