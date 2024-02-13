import numpy as np


def num_tokens_from_messages(messages, encoding, tokens_per_message=3, tokens_per_name=1):
    """
    Count the number of tokens in a list of messages.

    Args:
        messages (list): List of dictionaries, each containing a message.
        encoding (object): Encoding object from tiktoken.
        tokens_per_message (int): Number of tokens per message.
        tokens_per_name (int): Number of tokens per name.

    Returns:
        int: Total number of tokens in the messages.
    """
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # Adding tokens for start, end, and separator tokens
    return num_tokens


def num_assistant_tokens_from_messages(messages, encoding):
    """
    Count the number of tokens in assistant messages.

    Args:
        messages (list): List of dictionaries, each containing a message.
        encoding (object): Encoding object from tiktoken.

    Returns:
        int: Total number of tokens in the assistant messages.
    """
    num_tokens = 0
    for message in messages:
        if message["role"] == "assistant":
            num_tokens += len(encoding.encode(message["content"]))
    return num_tokens


def print_distribution(values, name):
    """
    Print distribution statistics of a list of values.

    Args:
        values (list): List of values.
        name (str): Name of the distribution.
    """
    print(f"\n#### Distribution of {name}:")
    print(f"min / max: {min(values)}, {max(values)}")
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")
    print(f"p5 / p95: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")
