import os

import tiktoken

from helpers.cost_estimation import cost_estimation
from helpers.data_loading import load_dataset
from helpers.data_warnings_and_token_counts import data_warnings_and_token_counts
from helpers.format_validation import validate_format

# Get the current working directory
directory_path = os.getcwd()

# Construct the path to the data_set directory
data_set_directory = os.path.join(directory_path, "data_set")

print("sssssssssssssssssssssssssssssssssssssssssssssssssssss")
print(data_set_directory)

# Construct the path to the JSON dataset file
json_file_path = os.path.join(data_set_directory, "dataset.jsonl")
print(json_file_path)

# Step 1: Load the dataset
dataset = load_dataset(data_path=json_file_path)

# Step 2: Validate the format
format_errors = validate_format(dataset)

# Step 3: Calculate warnings and token counts
encoding = tiktoken.get_encoding("cl100k_base")
results = data_warnings_and_token_counts(dataset, encoding)

# Step 4: Estimate the cost
cost_info = cost_estimation(dataset, results["num_total_tokens_per_example"])

# Step 5: Print the results
print("Format validation errors:", format_errors)
print("Warnings and token counts:", results)
print("Cost estimation:", cost_info)
