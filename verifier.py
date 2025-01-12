from dotenv import load_dotenv
import os
import json

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


def extract_output_and_reason(response_content):
    """
    Extracts 'output' and 'reason' from the response content by finding the JSON structure.

    Args:
        response_content (str): The response content as a string.

    Returns:
        tuple: A tuple containing 'output' and 'reason', or (None, None) if parsing fails.
    """
    # Find the first occurrence of '{' and '}'
    start_idx = response_content.find('{')
    end_idx = response_content.find('}')
    
    if start_idx != -1 and end_idx != -1:  # Ensure both braces are found
        valid_string = response_content[start_idx:end_idx+1]
        try:
            # Parse the JSON string
            parsed_response = json.loads(valid_string.strip())
            return parsed_response.get("output"), parsed_response.get("reason")
        except json.JSONDecodeError:
            return None, None  # Return None if JSON decoding fails
    else:
        return None, None 
# Function to generate output based on inputs
def verify_short_answer(question, claim, reference):
    # Read the template from the file
    template = read_prompt_template("verifier_prompt_v2.txt")
    
    # Construct the prompt
    prompt = create_prompt(question, claim, reference, template)
    
    retries = 5
    while retries > 0:
        retries -= 1
        # Make the API call
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=400,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # import pdb; pdb.set_trace()
        # Extract and parse the response
        answer_mapping = {
            "Contradiction": -1,  # Contradiction is mapped to wrong
            "entailment": 1,   # Entailment is mapped to correct
        }
        output,reason = extract_output_and_reason(response.content[0].text)
        if output and reason:  # If valid JSON was extracted, return it
            return answer_mapping[output],reason
        
        # If retries are exhausted and no valid data is extracted
    raise ValueError("Failed to generate valid JSON response after multiple retries.")

## Sample RUN
# question = "What is the purpose of Angular's RouterModule, and how is it used in an application?"
# claim = "The RouterModule is used to manage HTTP requests and responses in an Angular application."
# reference = "The RouterModule enables navigation between different components in an Angular application by defining routes. It is imported into the application module and configured with route definitions to map paths to components, facilitating seamless navigation."

# output,reason = verify_short_answer(question, claim, reference)
# print(output)
# print(reason)

# print(our_first_message.content[0].text)