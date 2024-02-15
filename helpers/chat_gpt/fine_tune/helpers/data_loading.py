import json

def load_dataset(data_path):
    """
    Load dataset from a JSONL file with error handling.

    Args:
        data_path (str): Path to the JSONL file.

    Returns:
        list: List of dictionaries, each containing a conversation, or an empty list in case of an error.
    """
    dataset = []
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    dataset.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from line: {line}\nError: {e}")
    except FileNotFoundError:
        print(f"The file was not found at the specified path: {data_path}")
        return []  # Return an empty list if file not found
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []  # Return an empty list in case of unexpected errors

    return dataset
