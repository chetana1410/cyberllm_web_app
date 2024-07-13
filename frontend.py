import streamlit as st
import requests
import time

def reset_session():
    st.session_state.uploaded_files = None
    st.session_state.uploading = False
    st.session_state.processing = False
    st.session_state.results_displayed = False
    st.session_state.elements = 0
    st.session_state.failed_files = []
    st.session_state["file_uploader_key"] = 0
    st.session_state["disable_upload"] = False
    st.session_state["disable_chat"] = True
    st.session_state.messages = []

def init_session():
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = None
    if 'uploading' not in st.session_state:
        st.session_state.uploading = False
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results_displayed' not in st.session_state:
        st.session_state.results_displayed = False
    if 'elements' not in st.session_state:
        st.session_state.elements = 0
    if 'failed_files' not in st.session_state:
        st.session_state.failed_files = []
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0
    if "disable_upload" not in st.session_state:
        st.session_state["disable_upload"] = False
    if "disable_chat" not in st.session_state:
        st.session_state["disable_chat"] = True
    if "messages" not in st.session_state:
        st.session_state.messages = []

def upload_documents():
    st.sidebar.title("Upload Documents")
    uploaded_files = st.sidebar.file_uploader("Upload documents", accept_multiple_files=True, key=st.session_state["file_uploader_key"], disabled=st.session_state["disable_upload"])
    col1, col2 = st.sidebar.columns(2)
    with col1:
        submit_button = st.sidebar.button("Submit", key='submit')
    with col2:
        reset_button = st.sidebar.button("Reset", key='reset')

    if uploaded_files and submit_button:
        total_files = len(uploaded_files)
        current_file_number = 0

        # Display a progress bar
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()

        files = [("files", file) for file in uploaded_files]

        for file in uploaded_files:
            current_file_number += 1
            status_text.text(f"Uploading file {current_file_number} of {total_files}: {file.name}")
            progress_bar.progress(current_file_number / total_files)

        response = requests.post("http://127.0.0.1:5000/upload", files=files)
        
        # Clear progress bar and status text once upload is done
        progress_bar.empty()
        status_text.empty()

        if response.status_code == 200:
            data = response.json()
            st.session_state.elements = data.get("elements")
            st.session_state.failed_files = data.get("failed_files")
            st.session_state.processing = False
            st.session_state.results_displayed = True
            st.session_state.disable_upload = True 
            st.session_state.disable_chat = False
            st.session_state["file_uploader_key"] += 1
            st.rerun()
        else:
            st.error(f"Failed to process files: {response.json().get('error')}")

    if reset_button:
        reset_session()
        st.rerun()

    # Display processing results
    if st.session_state.results_displayed:
        st.sidebar.write(f"Processed {st.session_state.elements} elements.")
        time.sleep(2)

        if st.session_state.failed_files:
            st.sidebar.error(f"The following files couldn't be processed: {', '.join(st.session_state.failed_files)}")

def chat_interface():
    st.title("Chat Interface")
    response = "Hello! I am CyberLLM. How can I assist you today?"
    with st.chat_message("AI"):
        st.markdown(response)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to human input
    if prompt := st.chat_input("Message CyberLLM?"):
        # Display human message in chat message container
        with st.chat_message("human"):
            st.markdown(prompt)

        response = requests.post("http://127.0.0.1:5000/chat", json={"history": st.session_state.messages, "query": prompt})

        # Add human message to chat history
        st.session_state.messages.append({"role": "human", "content": prompt})

        if response.status_code == 200:
            data = response.json()
            agent_answer = data.get('message', 'No response received.')
            # Display AI response in chat message container
            with st.chat_message("AI"):
                st.markdown(agent_answer)
            # Add AI response to chat history
            st.session_state.messages.append({"role": "AI", "content": agent_answer})
        else:
            st.session_state.messages.append({"role": "AI", "content": "Error: Failed to get response from the server."})
            with st.chat_message("AI"):
                st.markdown("Error: Failed to get response from the server.")

def evaluate_interface():
    st.title("Evaluate QA Pairs")
    uploaded_file = st.file_uploader("Upload CSV for Evaluation", type=["csv"], key="eval_uploader")

    col1, col2 = st.columns(2)
    with col1:
        submit_button = st.button("Submit Evaluation", key='submit_eval')
    with col2:
        reset_button = st.button("Reset Evaluation", key='reset_eval')

    if uploaded_file and submit_button:
        st.session_state.uploading = True
        with st.spinner("Evaluating..."):
            files = {"file": uploaded_file}
            response = requests.post("http://127.0.0.1:5000/evaluate", files=files)
            if response.status_code == 200:
                st.success("Evaluation completed. Download the results below.")
                st.download_button(
                    label="Download Evaluation Results",
                    data=response.content,
                    file_name='evaluation_results.csv',
                    mime='text/csv'
                )
            else:
                st.error(f"Failed to evaluate: {response.json().get('error')}")
        st.session_state.uploading = False

    if reset_button:
        reset_session()
        st.rerun()

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Chat Interface", "Evaluate QA Pairs"])

    init_session()

    upload_documents()

    if page == "Chat Interface":
        chat_interface()
    elif page == "Evaluate QA Pairs":
        evaluate_interface()

if __name__ == '__main__':
    main()
