def cost_estimation(
    dataset,
    convo_lens,
    max_tokens_per_example=4096,
    target_epochs=3,
    min_target_examples=100,
    max_target_examples=25000,
    min_default_epochs=1,
    max_default_epochs=25,
):
    """
    Estimate the cost and default number of epochs for training.

    Args:
        dataset (list): List of dictionaries, each containing a conversation.
        convo_lens (list): List of lengths of tokens in each conversation.
        max_tokens_per_example (int): Maximum number of tokens per example.
        target_epochs (int): Target number of epochs for training.
        min_target_examples (int): Minimum number of examples for the target epochs.
        max_target_examples (int): Maximum number of examples for the target epochs.
        min_default_epochs (int): Minimum default number of epochs.
        max_default_epochs (int): Maximum default number of epochs.

    Returns:
        dict: Dictionary containing cost estimation information.
    """
    n_epochs = target_epochs
    n_train_examples = len(dataset)

    if n_train_examples * target_epochs < min_target_examples:
        n_epochs = min(max_default_epochs, min_target_examples // n_train_examples)
    elif n_train_examples * target_epochs > max_target_examples:
        n_epochs = max(min_default_epochs, max_target_examples // n_train_examples)

    n_billing_tokens_in_dataset = sum(min(max_tokens_per_example, length) for length in convo_lens)
    cost_estimation_info = {
        "n_billing_tokens_in_dataset": n_billing_tokens_in_dataset,
        "default_epochs": n_epochs,
        "default_token_cost": n_epochs * n_billing_tokens_in_dataset,
    }

    return cost_estimation_info
