import streamlit as st
from agent_config import initialize_main_agent
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession
import asyncio
import PyPDF2
import io

load_dotenv()

st.set_page_config(
    page_title= "Cover Letter Generator",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)


# Session type
session_type = "persistent"

# Initializing our agents
def initialize_agent():
    """Initialize our Cover Letter Agent"""

    main_agent = initialize_main_agent(examples_dir="examples")

    return main_agent

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def get_session(self, session_id: str, db_file: str = "cover_letter.db"):
        """Get or create a session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = SQLiteSession(session_id, db_file)
        return self.sessions[session_id]
    
    async def clear_session(self, session_id: str):
        """Clear a specific session"""
        if session_id in self.sessions:
            await self.sessions[session_id].clear_session()
            del self.sessions[session_id]
    
    async def get_session_items(self, session_id: str, limit: int = None):
        """Get conversation items from a session"""
        if session_id in self.sessions:
            return await self.sessions[session_id].get_items(limit=limit)
        return []
    
# Initialize the session manager
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

# Main UI
def main():
    st.title("Cover Letter Generator")
    st.write("Generate Professional Cover Letters Easily")

    # initialize our agents
    main_agent = initialize_agent()

    # session configuration sidebar
    with st.sidebar:
        st.header("⚙️ Session Configuration")

        agent_type = st.selectbox(
            "Select Agent Type",
            ["Basic"]
        )

        st.divider()

        st.subheader("Session Controls")

        if st.button("🗑️ Clear All Sessions"):
            with st.spinner("Clearing sessions..."):
                for session_id in list(st.session_state.session_manager.sessions.keys()):
                    asyncio.run(st.session_state.session_manager.clear_session(session_id))
                st.success("All sessions cleared!")
                st.rerun()

    # check for agent type, more to be added
    if agent_type == "Basic":
        render_basic_agent(main_agent)

def render_basic_agent(agent):
    """Render the basic agent """
    # User inputs
    name = st.text_input("Enter your name:")
    position = st.text_input("Position that you are applying for:")
    job_description = st.text_area("Job description from website:")
    current_resume = st.file_uploader("Upload Resume", type=["pdf"])
    skills = st.text_input("Key skills (comma-separated, optional):")
    additional_info = st.text_area("Additional details (optional):")

    if current_resume is not None:
        # read the file into bytes
        bytes_io = io.BytesIO(current_resume.getvalue())

        # read the pdf using PyPDF2
        pdf_reader = PyPDF2.PdfReader(bytes_io)
        
        st.success(f"Successfully uploaded {current_resume.name}")
        st.write(f"The PDF has {len(pdf_reader.pages)} pages.")

        # extract the text from the first page
        first_page_text = pdf_reader.pages[0].extract_text()

    generate = st.button("Generate Cover Letter")

    if generate and name and position and job_description and current_resume:
        # compose a single user_input string from all provided fields
        user_input = f"Name: {name}\nPosition: {position}\n\nJob Description:\n{job_description}\n\n"

        # include extracted resume text if available
        try:
            user_input += f"Resume Text (first page):\n{first_page_text}\n\n"
        except NameError:
            user_input += "Resume Text (first page):\n<could not extract>\n\n"

        # add skills and additional_info if available
        if skills:
            user_input += f"Skills: {skills}\n\n"

        if additional_info:
            user_input += f"Additional Info:\n{additional_info}\n\n"

        # generate the cover letter
        with st.spinner(f"Generating cover letter for {name} applying to {position}..."):
            session = st.session_state.session_manager.get_session(session_type, "cover_letter.db")
            result = asyncio.run(Runner.run(agent, user_input, session=session))

            st.success("Message sent!")
            st.write(f"**Assistant:** {result.final_output}")
    elif generate:
        st.info("❌Please provide input for the above fields❌")

    if st.button("📧 Show Previous Cover Letters", key="show_persistent"):
            items = asyncio.run(st.session_state.session_manager.get_session_items(session_type))
            
            assistant_items = [
                item for item in items if item.get("role") == "assistant"
            ]

            if assistant_items:
                st.write("**Generated Cover Letters:**")
                for item in assistant_items:
                    st.write(item["content"][0]["text"])
                    st.divider()

            else:
                st.info("No generated cover letters yet.")
        
    

def render_footer():
    st.divider()
    st.markdown("""
    ### Generate a starter cover letter easily
                
    The agents are shown as below, choose the one that fits best for you.
    
    1. **Basic**: Basic agent with in-memory and persistant sessions
        - Input: name, position, job description, and resume
    
    """)

if __name__ == "__main__":
    main()
    render_footer()