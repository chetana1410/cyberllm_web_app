from flask import Flask, render_template, redirect, request, session, jsonify, send_file
from google.cloud import storage
from tempfile import NamedTemporaryFile
import os
import uuid
import pandas as pd
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

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded CSV file to a temporary file
    with NamedTemporaryFile(delete=False) as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(tmp_file_path)

        # Check if the necessary columns are present
        required_columns = ['question', 'ground_truth', 'contexts']
        if not all(column in df.columns for column in required_columns):
            return jsonify({"error": "CSV file must contain 'question', 'ground_truth', and 'contexts' columns"}), 400

        # Remove the ground_truth column if it exists
        if 'answer' in df.columns:
            df = df.drop(columns=['answer'])

        # Generate ground_truth answers using the LLM
        df['answer'] = df.apply(lambda row: get_final_answer(row['contexts'], row['question']), axis=1)

        # Evaluate each row and append results
        evaluation_results = []
        for index, row in df.iterrows():
            evaluation_result = evaluate_question_answer(row['question'], row['ground_truth'], row['answer'], row['contexts'])
            evaluation_results.append(evaluation_result.to_dict(orient='records')[0])  # Convert to dict format for appending

        # Convert evaluation results to DataFrame and concatenate with original DataFrame
        eval_df = pd.DataFrame(evaluation_results)
        result_df = pd.concat([df, eval_df], axis=1)

        # Save the result DataFrame to a new CSV file
        result_file_path = tmp_file_path + "_result.csv"
        result_df.to_csv(result_file_path, index=False)

        return send_file(result_file_path, as_attachment=True, download_name='evaluation_results.csv')

    finally:
        os.remove(tmp_file_path)

if __name__ == '__main__':
    app.run(debug=True)
