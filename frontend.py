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

def upload_documents():
    with st.sidebar.expander("Upload Documents", expanded=True):
        uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True, key=st.session_state["file_uploader_key"], disabled=st.session_state["disable_upload"])
        col1, col2 = st.sidebar.columns(2)
        with col1:
            submit_button = st.button("Submit", key='submit')
        with col2:
            reset_button = st.button("Reset", key='reset')

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
    response = "Hello! I am CyberLLM. How can I assit you today"
    with st.chat_message("AI"):
        st.markdown(response)
    # if not st.session_state.elements:
    #     st.write("Upload at least one document to enable chat functionality.")
    # st.text_area("Chat here", disabled=st.session_state["disable_chat"])
    # st.text_area("", placeholder="Start typing...",height=20)
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
        
        # response = f"{prompt}"

        if response.status_code == 200:
            print('athu')
            data = response.json()
            agent_answer = data['message']
            # Display AI response in chat message container
            with st.chat_message("AI"):
                st.markdown(agent_answer)
            # Add AI response to chat history
            st.session_state.messages.append({"role": "AI", "content": agent_answer})


def main():
    st.sidebar.title("Document Upload")
    init_session()
    upload_documents()
    chat_interface()

if __name__ == '__main__':
    main()