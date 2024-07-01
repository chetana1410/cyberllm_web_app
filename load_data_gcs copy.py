import json
from google.cloud import storage
from unstructured.staging.base import dict_to_elements
from typing import Iterable, Optional
from google.cloud import storage

key_path = "keys.json"
storage_client = storage.Client.from_service_account_json(key_path)


def read_unstructured_json_files(bucket_name, organizations , prefix):
    # Initialize a storage client
    storage_client = storage.Client()
            
    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)
    
    elements = []
        
    for org in organizations:

        # List all objects that match the prefix
        blobs = bucket.list_blobs(prefix=prefix.format(org))
        cnt = 0
        for blob in blobs:
            if blob.name.endswith('.json'):
                # Download the contents of the blob as a string
                json_data = blob.download_as_string()
                # Load string data as JSON
                json_content = json.loads(json_data)
                for content in json_content:
                    content['metadata']['organization'] = org
                # convert json content to element class
                element = dict_to_elements(json_content)
                # append into list
                elements.extend(element)
                cnt+=1
                if cnt==10:
                    break
       

    return elements