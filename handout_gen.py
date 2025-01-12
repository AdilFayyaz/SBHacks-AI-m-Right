from dotenv import load_dotenv
import os
import json

load_dotenv()
my_api_key = os.getenv("CLAUDE_API")


from anthropic import Anthropic

client = Anthropic(
    api_key=my_api_key
)


# Function to read the prompt template from a text file
def read_prompt_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to create the prompt by replacing placeholders
def create_prompt(passage, template):
    prompt = template.replace("<passage>", passage)
    return prompt

def extract_output(response_content):
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

            return parsed_response.get("output")
        except json.JSONDecodeError:
            return None, None  # Return None if JSON decoding fails
    else:
        return None, None 
    
    
# Function to generate output based on inputs
def generate_handout(context):
    # Read the template from the file
    template = read_prompt_template("handout_gen_prompt.txt")
    
    # Construct the prompt
    prompt = create_prompt(context, template)
    
    retries = 5
    while retries > 0:
        retries -= 1
        # Make the API call
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        extracted_details = extract_output(response.content[0].text)
        if extracted_details != (None,None):  # If valid JSON was extracted, return it
            return extracted_details
        
        # If retries are exhausted and no valid data is extracted
    raise ValueError("Failed to generate valid JSON response after multiple retries.")

# Sample RUN
passage = "The Document Object Model (DOM) is a programming interface for web documents. It represents the structure of a web page as a tree of objects, each corresponding to a part of the page, such as elements, attributes, and text content. In Angular, the DOM plays a crucial role in rendering components and handling user interactions. Angular’s change detection mechanism updates the DOM efficiently, ensuring that only the necessary elements are re-rendered when the component's data changes. This dynamic interaction between the component’s state and the DOM is at the core of Angular's declarative rendering approach. Furthermore, Angular provides tools like Renderer2 to safely interact with the DOM, which helps abstract away browser-specific differences and improves security by preventing potential cross-site scripting (XSS) vulnerabilities. Understanding how Angular interacts with the DOM is key to optimizing application performance and ensuring seamless user experiences."

extracted_details= generate_handout(passage)
print(extracted_details)
