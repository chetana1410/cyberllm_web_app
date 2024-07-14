from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel
import prompts
import importlib
importlib.reload(prompts)
from prompts import final_answer_prompt, generate_qa_prompt

def get_final_answer(context: str, query: str) -> str:
    project = "736225251813"
    endpoint_id = "gemini-1.5-pro-001"
    location = "us-central1"
    key_path = "application_default_credentials.json"

    # Define the prompt
    prompt = final_answer_prompt.format(context = context, query = query)

    # Initialize Vertex AI with the specified project and location
    vertexai.init(project=project, location=location)

    # Instantiate the generative model
    model = GenerativeModel(model_name=endpoint_id)

    # Define the generation configuration
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.1,
        "top_p": 0.95,
    }

    # Generate the response
    responses = model.generate_content(
        [prompt],
        generation_config=generation_config,
        stream=True,
    )
    # return responses

    # Collect the generated response
    response_content = ""
    for part in responses:
        response_content += part.text

    return response_content

# def get_hyde_passage(query: str) -> str:
#     project = "736225251813"
#     endpoint_id = "gemini-1.5-pro-001"
#     location = "us-central1"
#     key_path = "application_default_credentials.json"

#     # Define the prompt
#     prompt = hyde_prompt.format(query = query)

#     # Initialize Vertex AI with the specified project and location
#     vertexai.init(project=project, location=location)

#     # Instantiate the generative model
#     model = GenerativeModel(model_name=endpoint_id)

#     # Define the generation configuration
#     generation_config = {
#         "max_output_tokens": 1500,
#         "temperature": 0.1,
#         "top_p": 0.95,
#     }

#     # Generate the response
#     responses = model.generate_content(
#         [prompt],
#         generation_config=generation_config,
#         stream=True,
#     )
#     # return responses

#     # Collect the generated response
#     response_content = ""
#     for part in responses:
#         response_content += part.text

#     return response_content

def generate_qa(chunks: str):
    project = "736225251813"
    endpoint_id = "gemini-1.5-pro-001"
    location = "us-central1"
    key_path = "application_default_credentials.json"

    # Define the prompt
    prompt = generate_qa_prompt.format(chunkss = chunks)

    # Initialize Vertex AI with the specified project and location
    vertexai.init(project=project, location=location)

    # Instantiate the generative model
    model = GenerativeModel(model_name=endpoint_id)

    # Define the generation configuration
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.1,
        "top_p": 0.95,
    }

    # Generate the response
    responses = model.generate_content(
        [prompt],
        generation_config=generation_config,
        stream=True,
    )
    # return responses

    # Collect the generated response
    response_content = ""
    for part in responses:
        response_content += part.text

    return response_content

