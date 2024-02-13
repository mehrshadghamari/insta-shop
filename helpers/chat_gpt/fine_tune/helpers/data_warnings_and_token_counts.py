from helpers.chat_gpt.fine_tune.helpers.token_counting_utilities import num_assistant_tokens_from_messages
from helpers.chat_gpt.fine_tune.helpers.token_counting_utilities import num_tokens_from_messages


def data_warnings_and_token_counts(dataset, encoding):
    """
    Calculate warnings and token counts for the dataset.

    Args:
        dataset (list): List of dictionaries, each containing a conversation.
        encoding (object): Encoding object from tiktoken.

    Returns:
        dict: Dictionary containing warnings and token counts.
    """
    n_missing_system = 0
    n_missing_user = 0
    n_messages = []
    convo_lens = []
    assistant_message_lens = []

    for ex in dataset:
        messages = ex["messages"]
        if not any(message["role"] == "system" for message in messages):
            n_missing_system += 1
        if not any(message["role"] == "user" for message in messages):
            n_missing_user += 1
        n_messages.append(len(messages))
        convo_lens.append(num_tokens_from_messages(messages, encoding))
        assistant_message_lens.append(num_assistant_tokens_from_messages(messages, encoding))

    results = {}
    results["n_missing_system"] = n_missing_system
    results["n_missing_user"] = n_missing_user
    results["num_messages_per_example"] = n_messages
    results["num_total_tokens_per_example"] = convo_lens
    results["num_assistant_tokens_per_example"] = assistant_message_lens
    results["n_too_long"] = sum(l > 4096 for l in convo_lens)

    return results
