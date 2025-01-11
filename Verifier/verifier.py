from dotenv import load_dotenv
import os

load_dotenv()
my_api_key = os.getenv("CLAUDE_API")


from anthropic import Anthropic

client = Anthropic(
    api_key=my_api_key
)


# our_first_message = client.messages.create(
#     model="claude-3-haiku-20240307",
#     max_tokens=1000,
#     messages=[
#         {"role": "user", "content": "Hi there! Please write me a haiku about a pet chicken"}
#     ]
# )



# Function to read the prompt template from a text file
def read_prompt_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to create the prompt by replacing placeholders
def create_prompt(question, claim, reference, template):
    prompt = template.replace("<question>", question)
    prompt = prompt.replace("<claim>", claim)
    prompt = prompt.replace("<reference>", reference)
    return prompt

# Function to generate output based on inputs
def generate_output(question, claim, reference, template_file):
    # Read the template from the file
    template = read_prompt_template(template_file)
    
    # Construct the prompt
    prompt = create_prompt(question, claim, reference, template)
    
    # Make the API call
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Return the output text
    return response.content[0].text


# Example usage
template_file = "verifier_prompt.txt"  # File containing the template with placeholders
question = "What is the lifespan of a chicken?"
claim = "Chickens can live up to 10 years."
reference = "Backyard Poultry Magazine, 2023."

output = generate_output(question, claim, reference, template_file)
print(output)

# print(our_first_message.content[0].text)