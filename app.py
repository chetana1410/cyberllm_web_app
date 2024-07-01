import os
import json
from flask import Flask, render_template, redirect, request, session , jsonify
from flask_session import Session
from google.cloud import storage
from tempfile import NamedTemporaryFile
from preprocess_save_documents import preprocess_document
from google.oauth2 import service_account
from load_data_gcs import read_json_files_from_gcs
from metadata_llm import generate_metadata
from langchain_chroma import Chroma
from chunking import unstructured_chunk_by_title
from langchain_core.documents import Document
from langchain.vectorstores import utils as chromautils
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.vectorstores import utils as chromautils
from gemini_final_answer import get_final_answer



app = Flask(__name__)

# Initialize GCS client
key_path = "keys.json"
client = storage.Client.from_service_account_json(key_path)
# client = storage.Client(credentials=credentials)
bucket_name = 'ai_llm'
folder_name = 'test_pipeline1'


elements = []
documents = []

# Initialize the SentenceTransformers model
model_name = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(model_name)


# Define a custom embedding class with the required method
class CustomEmbeddings:
    def embed_documents(self, texts):
        return embedding_model.encode(texts).tolist()  # Convert to list

    def embed_query(self, text):
        return embedding_model.encode([text]).tolist()[0]  # Convert to list and return single embedding
    

@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist('files')
    failed_files = [] 

    for file in files:
        if file.filename == '':
            failed_files.append("Unnamed file")
            continue

        with NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.read())
            tmp_file_path = tmp_file.name

        try:
            element = preprocess_document(tmp_file_path)
            elements.extend(element)
        except Exception as e:
            failed_files.append(file.filename)
        finally:
            os.remove(tmp_file_path)

    chunks = unstructured_chunk_by_title(elements,2000,200)
    idx = 0
    print(len(chunks))
    while idx<len(chunks):
        element = chunks[idx]
        text = element.text
        metadata = element.metadata.to_dict()
        del metadata["languages"]
        # metadata["source"] = metadata["filename"]
        documents.append(Document(page_content=text, metadata=metadata))
        print(f'Chunk {idx} Done')
        idx+=1

    response = {
        "elements": len(documents),
        "failed_files": len(failed_files)
    }

    return jsonify(response)

@app.route('/chat', methods=['POST'])
def chat():

    chat_history = request.json.get("history", [])
    user_question = request.json.get("query", "")
    docs = chromautils.filter_complex_metadata(documents)  # try using vector store which supports list metadata as keywords are important
    vectorstore = Chroma.from_documents(documents=docs, embedding=CustomEmbeddings())
    retriever = vectorstore.as_retriever()
    retrieved_docs  = retriever.get_relevant_documents(user_question)
    context = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(retrieved_docs)])
    answer = get_final_answer(context,user_question)
    # Handle the chat history here
    # For example, you can save it to a database or process it
    return jsonify({"status": "success", "message": answer})

if __name__ == '__main__':
    app.run(debug=True)



