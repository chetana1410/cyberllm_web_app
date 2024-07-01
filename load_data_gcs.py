import json
from google.cloud import storage
from unstructured.staging.base import dict_to_elements
from typing import Iterable, Optional
from google.cloud import storage

key_path = "keys.json"
storage_client = storage.Client.from_service_account_json(key_path)


def read_json_files_from_gcs(bucket_name, prefix):
    # Initialize a storage client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # List all objects that match the prefix
    blobs = bucket.list_blobs(prefix=prefix)

    elements = []
    for blob in blobs:
        if blob.name.endswith('.json'):
            # Download the contents of the blob as a string
            json_data = blob.download_as_string()
            # # Load string data as JSON
            json_content = json.loads(json_data)
            element = dict_to_elements(json_content)
            elements.extend(element)

    return elements

