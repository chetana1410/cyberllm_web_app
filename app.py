from flask import Flask, render_template, redirect, request, session, jsonify
from google.cloud import storage
from tempfile import NamedTemporaryFile
import os
import uuid
from preprocess_save_documents import preprocess_document
from chunking import unstructured_chunk_by_title
from langchain_core.documents import Document
from vectorstore import pinecone_langc_doc, query_pinecone
from embeddings import embed_doc
from evaluation import evaluate_question_answer
from gemini_final_answer import get_final_answer

app = Flask(__name__)

# Initialize GCS client
key_path = "keys.json"
client = storage.Client.from_service_account_json(key_path)
bucket_name = 'ai_llm'
folder_name = 'test_pipeline1'

elements = []
documents = []

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

    chunks = unstructured_chunk_by_title(elements, 2000, 200)
    for idx, element in enumerate(chunks):
        text = element.text
        metadata = element.metadata.to_dict()
        del metadata["languages"]
        documents.append(Document(page_content=text, metadata=metadata))
        print(f'Chunk {idx} Done')
    
    pinecone_langc_doc("example1", documents, "ns6")

    response = {
        "elements": len(documents),
        "failed_files": len(failed_files)
    }

    return jsonify(response)

@app.route('/chat', methods=['POST'])
def chat():
    user_question = request.json.get("query", "")
    
    output = query_pinecone("example1", user_question, "ns6", 4)
    context = " ".join([f"({idx + 1}). {item['metadata']['text']}" for idx, item in enumerate(output)])
    answer = get_final_answer(context, user_question)

    ground_truth = answer
    evaluation_results = evaluate_question_answer(user_question, ground_truth, answer, context)

    evaluation_str = "\n".join([f"**{key}**: {value}\n" for key, value in evaluation_results.iloc[0].items()])
    final_response = f"# Answer:\n {answer}\n\n # Evaluation:\n{evaluation_str}"

    response = {
        "status": "success",
        "message": final_response
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
