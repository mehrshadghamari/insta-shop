import openai
from helpers.data_loading import load_dataset


# Set your OpenAI API key
api_key = 'YOUR_API_KEY'
openai.api_key = api_key

# Define your dataset

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

# Fine-tune the model
response = openai.FineTune.create(
    model="text-davinci-003",  # Choose the model you want to fine-tune
    data=dataset,
    n_epochs=3,  # Number of epochs for fine-tuning
    learning_rate=1e-5,  # Learning rate for fine-tuning
    validation_percentage=10,  # Percentage of dataset to use for validation
    validation_interval=500,  # Validation interval
    callbacks={"checkpoint": {"save_every_n": 1000}},  # Callbacks for saving checkpoints
)
print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
# Print response from the API
print(response)