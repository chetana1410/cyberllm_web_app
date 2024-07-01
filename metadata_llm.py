#with gemini

import json
from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models



def generate_metadata(endpoint_id,prompt,text):

    vertexai.init(project="aristiun-webapp", location="us-central1")
    model = GenerativeModel(endpoint_id)
    
    safety_config = [
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
    ),
]

    generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0,
    "top_p": 0.95,
    }  

    responses = model.generate_content(

        [prompt.format(text)],
         safety_settings=safety_config,
         generation_config=generation_config,
         stream=True,
    )
    
    answer = ""
    for response in responses:
        answer += response.text
        
    #Clean up the string
    clean_answer = answer.replace("```json", "").replace("```", "")
    # print(clean_answer)
    # print('='*100)
    metadata = json.loads(clean_answer)
    return metadata
   