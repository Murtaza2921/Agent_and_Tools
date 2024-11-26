import streamlit as st
import requests
import os

# Streamlit app configuration
st.set_page_config(
    page_title="Super Cool Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS for styling
st.markdown(
    """
    <style>
    .chat-container { max-width: 700px; margin: auto; }
    .user-bubble { background-color: #007bff; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right; }
    .bot-bubble { background-color: #f1f0f0; color: black; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; }
    .upload-container { margin: 20px auto; max-width: 700px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; text-align: center; }
    .scrollable { max-height: 80vh; overflow-y: auto; margin-bottom: 20px; padding: 10px; border-radius: 5px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown('<div class="chat-container"><h1>🤖 Super Cool Chatbot</h1></div>', unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Document Upload Section
st.markdown('<div class="upload-container"><h2>📂 Upload Document for Knowledge Base</h2></div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a PDF, Word, or CSV file:", type=["pdf", "docx", "csv"])

if uploaded_file:
    # Ensure the uploaded_files directory exists
    os.makedirs("uploaded_files", exist_ok=True)
    
    file_path = os.path.join("uploaded_files", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    with st.spinner("Adding file to knowledge base..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/upload",
                files={"file": open(file_path, "rb")},
            )
            if response.status_code == 200:
                st.success(f"File '{uploaded_file.name}' added to the knowledge base!")
            else:
                st.error("Failed to add file to knowledge base.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Chat interaction
st.markdown('<div class="chat-container scrollable">', unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Initialize user_query in session state if not already
if "user_query" not in st.session_state:
    st.session_state["user_query"] = ""

# Clear the user input flag
if "clear_input" not in st.session_state:
    st.session_state["clear_input"] = False

# Handle the input form and reset the user query after submission
with st.form(key="chat_form"):
    user_query = st.text_input(
        "Your message:",
        placeholder="Type something...",
        value=st.session_state["user_query"],  # Ensure the input widget is in sync with session state
        key="user_query",
        label_visibility="collapsed",
    )
    submit_button = st.form_submit_button("Send")

# Process the form submission
if submit_button and user_query.strip():
    st.session_state["messages"].append({"role": "user", "content": user_query})

    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={"query": user_query},
            )
            bot_reply = response.json().get("response", "Sorry, something went wrong!")
        except Exception as e:
            bot_reply = f"Error: {str(e)}"

    st.session_state["messages"].append({"role": "bot", "content": bot_reply})

    # Set the flag to clear input after the submission
    st.session_state["clear_input"] = True

# Clear the input field after form submission (before rerun)
if st.session_state["clear_input"]:
    #st.session_state["user_query"] = ""  # Reset the user query
    st.session_state["clear_input"] = False  # Reset the clear flag
    # Optionally, you can add a rerun here if needed
    # st.experimental_rerun()
