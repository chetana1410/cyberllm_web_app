import json
from typing import Iterable, Optional
from handle_cleaning import clean_elements
from unstructured.documents.elements import Element
from unstructured.partition.auto import partition, partition_html
# from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json, _fix_metadata_field_precision, elements_to_dicts


def preprocess_document(file):
    elements = partition(file, unique_element_ids=True, Strategies='hi_res')
    elements = clean_elements(elements)
    return elements
    # dict_output = elements_to_dicts(elements)
    # return dict_output



def upload_to_cloud(text,bucket_name,folder_name,file_name, storage_client):
    print(bucket_name,folder_name,file_name)
    print("--"*100)
    # print(text,bucket_name,folder_name,file_name)
    bucket = storage_client.get_bucket(bucket_name)
    print("PRINT BUCKET:", bucket)
    blob_path = f"{folder_name}/{file_name.split('/')[-1]}"
    print(blob_path)
    print(text)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(text, content_type='application/json')


def elements_to_json(
        elements: Iterable[Element],
        # filename: Optional[str] = None,
        indent: int = 4,
        encoding: str = "utf-8",
) -> Optional[str]:
    """Saves a list of elements to a JSON file if filename is specified.

    Otherwise, return the list of elements as a string.
    """
    # -- serialize `elements` as a JSON array (str) --
    precision_adjusted_elements = _fix_metadata_field_precision(elements)
    element_dicts = elements_to_dicts(precision_adjusted_elements)
    json_str = json.dumps(element_dicts, ensure_ascii=False, indent=indent, sort_keys=True)
    return json_str

