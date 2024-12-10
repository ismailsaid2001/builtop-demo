import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8000"  # Replace with your FastAPI URL
BUILTOP_LOGO_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQY7gSQHO6a8dUjEOcYXbc7q-za2ZMlD03gkA&s"  # Replace with your actual logo URL
YELLOW = "#FFD700"
BLACK = "#000000"

# Streamlit configuration
st.set_page_config(
    page_title="BuiltOp Contractors QA",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar with logo and title
st.sidebar.image(BUILTOP_LOGO_URL, use_column_width=True)
st.sidebar.title("BuiltOp Contractors QA")
st.sidebar.markdown("### Efficiently analyze and manage RFPs!")

# Header
st.markdown(
    f"""
    <div style="background-color:{BLACK}; padding:10px; border-radius:10px; margin-bottom:20px;">
        <h1 style="color:{YELLOW}; text-align:center;">Welcome to BuiltOp Contractors QA</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Set up the FastAPI base URL
API_BASE_URL = "http://127.0.0.1:8000"  # Replace with your FastAPI URL

st.title("Contractors QA Chatbot")

# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Step 1: Create a session
if st.session_state.session_id is None:
    if st.button("Create New Session"):
        response = requests.post(f"{API_BASE_URL}/session/create")
        if response.status_code == 200:
            st.session_state.session_id = response.json()["session_id"]
            st.success(f"Session created: {st.session_state.session_id}")
        else:
            st.error("Failed to create session. Please try again.")

# Ensure session is created
if st.session_state.session_id:
    st.write(f"Session ID: {st.session_state.session_id}")

    # Step 2: Set Language
    language = st.text_input("Enter Language Code (e.g., 'en' for English, 'ar' for Arabic)", "en")
    if st.button("Set Language"):
        response = requests.post(
            f"{API_BASE_URL}/session/{st.session_state.session_id}/set-language",
            params={"language": language},  # Use params for query parameters
        )
        if response.status_code == 200:
            st.success(f"Language set to {language} for session {st.session_state.session_id}")
        else:
            st.error("Failed to set language. Please try again.")

    # Step 3: Upload RFP
    uploaded_file = st.file_uploader("Upload an RFP Document", type=["pdf", "txt"])
    if uploaded_file and st.button("Upload and Analyze RFP"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(
            f"{API_BASE_URL}/session/{st.session_state.session_id}/upload-rfp",
            files=files,
        )
        if response.status_code == 200:
            st.success("RFP uploaded and analyzed successfully.")
            st.json(response.json()['analysis'])
        else:
            st.error("Failed to upload and analyze RFP. Please try again.")

if st.button("Match Contractors"):
    # Send a request to the backend to get the matching contractors
    response = requests.get(
        f"{API_BASE_URL}/session/{st.session_state.session_id}/match-contractors"
    )
    if response.status_code == 200:
        # If the request is successful, show the matching contractors
        matching_analysis = response.json().get('matching_analysis')
        if matching_analysis:
            # Extracting top matching contractors
            top_contractors = matching_analysis.get("top_matching_contractors", [])

            # If there are contractors, create a DataFrame
            if top_contractors:
                contractors_data = []
                for contractor in top_contractors:
                    contractors_data.append({
                        "Company Name": contractor["company_name"],
                        "Reasoning": contractor["reasoning"]
                    })

                # Convert to DataFrame
                contractors_df = pd.DataFrame(contractors_data)

                # Display the table using Streamlit's dataframe
                st.subheader("Top Matching Contractors")
                st.dataframe(contractors_df, width=3000)
            else:
                st.error("No contractors found in the matching analysis.")
        else:
            st.error("No matching analysis found.")
    else:
        st.error("Failed to match contractors. Please try again.")

# Step 5: Chatbot Interaction
st.subheader("Chat with the Bot")

# Displaying chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages from both the user and the bot
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.write(f"**You**: {msg['content']}")
    elif msg['role'] == 'bot':
        st.write(f"**Bot**: {msg['content']}")

# Input for new question
question = st.text_input("Ask a Question")

if st.button("Submit Question"):
    if question.strip():
        # Add user question to chat history
        st.session_state.messages.append({"role": "user", "content": question})

        # Use a spinner while waiting for the response
        with st.spinner("Fetching response from the bot..."):
            # Send the question to the FastAPI backend
            response = requests.post(
                f"{API_BASE_URL}/session/{st.session_state.session_id}/ask",
                json={"text": question},  # Send the question as part of the JSON body
            )
            if response.status_code == 200:
                answer = response.json()  # Get the response as JSON
                answer_text = answer.get("answer", "No answer available.")

                # Add bot answer to chat history
                st.session_state.messages.append({"role": "bot", "content": answer_text})

                # Display bot's answer
                st.write(f"**Bot**: {answer_text}")
            else:
                st.error("Failed to retrieve an answer.")
    else:
        st.warning("Please enter a question.")
