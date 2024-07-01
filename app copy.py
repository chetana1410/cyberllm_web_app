import os
import json
from flask import Flask, render_template, redirect, request, session , jsonify
from flask_session import Session
from google.cloud import storage
from tempfile import NamedTemporaryFile
from preprocess_save_documents import preprocess_document
from google.oauth2 import service_account
from load_data_gcs import read_json_files_from_gcs
from prompts import prompt_metadata_gemini 
from metadata_llm import generate_metadata
import bs4
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chunking import unstructured_chunk_by_title
from langchain_core.documents import Document
from langchain.vectorstores import utils as chromautils
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.vectorstores import utils as chromautils

from langchain_google_vertexai import HarmBlockThreshold, HarmCategory
from langchain_google_vertexai import VertexAI
import vertexai

from gemini_final_answer import get_final_answer


# ### Contextualize question ###
# contextualize_q_system_prompt = """Given a chat history and the latest user question \
# which might reference context in the chat history, formulate a standalone question \
# which can be understood without the chat history. Do NOT answer the question, \
# just reformulate it if needed and otherwise return it as is."""
# contextualize_q_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", contextualize_q_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )

# ### Answer question ###
# system = """You're a helpful AI assistant. Given a user question and some Wikipedia article snippets, \
# answer the user question and provide citations. If none of the articles answer the question, just say you don't know.

# Remember, you must return both an answer and citations. A citation consists of a VERBATIM quote that \
# justifies the answer and the ID of the quote article. Return a citation for every quote across all articles \
# that justify the answer. Use the following format for your final output:

# <cited_answer>
#     <answer></answer>
#     <citations>
#         <citation><source_id></source_id><quote></quote></citation>
#         <citation><source_id></source_id><quote></quote></citation>
#         ...
#     </citations>
# </cited_answer>

# Here are the Wikipedia articles:{context}"""
# qa_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )


app = Flask(__name__)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

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
        # prompt = prompt_metadata_gemini
        # try:
        #     extra_metadata = generate_metadata(endpoint_id,prompt,text)
        # except ResourceExhausted as e:
        #     print('Resourse Exhausted..Sleeping for 10 sec')
        #     time.sleep(10)
        #     idx-=1
        #     #extra_metadata = generate_metadata(endpoint_id,prompt,text)
        # except Exception as e:
        #     # Handle any other exceptions not caught by the previous blocks
        #     print(f"An error occurred: {e}")
        # idx+=1
            
        # cleaned_text = extra_metadata['cleaned_text']
        # for key in extra_metadata.keys():
        #     if key!='cleaned_text':
        #         metadata[key] = extra_metadata[key]
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

    # history_aware_retriever = create_history_aware_retriever(
    #     llm, retriever, contextualize_q_prompt
    # )


    # question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    # rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # conversational_rag_chain = RunnableWithMessageHistory(
    #     rag_chain,
    #     chat_history,
    #     input_messages_key="input",
    #     history_messages_key="chat_history",
    #     output_messages_key="answer",
    # )

    # answer = conversational_rag_chain.invoke(
    #         {"input": user_question}
    #                                         )
    retrieved_docs  = retriever.get_relevant_documents(user_question)
    context = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(retrieved_docs)])
    answer = get_final_answer(context,user_question)
    # Handle the chat history here
    # For example, you can save it to a database or process it
    return jsonify({"status": "success", "message": answer})


    # dict_output = preprocess_document(tmp_file_path)
    # json_output = json.dumps(dict_output)
    # file_name = file.filename.split('/')[-1].split('.')[0] + ".json"
    # gcs_file_path = f"{folder_name}/{file_name}"

    # try:
    #     print(f"Attempting to write to GCS: {gcs_file_path}")
    #     bucket = client.bucket(bucket_name)
    #     blob = bucket.blob(gcs_file_path)
    #     blob.upload_from_string(json_output, content_type="application/json")
    #     print("Uploaded successfully!")
    # except Exception as e:
    #     print(f"Error occurred: {e}")
    #     return jsonify({"error": str(e)}), 500
    # finally:
    #     os.remove(tmp_file_path)

    # return jsonify({"message": f"Processed and uploaded: {file_name}"}), 200

if __name__ == '__main__':
    app.run(debug=True)



