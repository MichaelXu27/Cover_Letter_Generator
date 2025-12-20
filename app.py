import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession
import asyncio

load_dotenv()

st.set_page_config(
    page_title= "Cover Letter Generator",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)



def initialize_agent():
    """Initialize our Cover Letter Agent"""

    main_agent = Agent(
        name="Cover Letter Agent",
        instructions="""
        You are a helping assistant for writing cover letters based on the user inputted name, email, linkedin job description, as well as some presupplied example cover letters.

        Remember previous conversation context and reference it when relevant. The user may as you to refine some aspects so just be aware of that. 
        Be friendly and professional.
        """
    )

    return main_agent

# Main UI
def main():
    st.title("Cover Letter Generator")
    st.write("Generate Professional Cover Letters Easily")

    main_agent = initialize_agent()

    with st.sidebar:
        st.header("⚙️ Session Configuration")

        agent_type = st.selectbox(
            "Select Agent Type",
            ["Basic"]
        )

        if agent_type == "Basic":
            session_type = st.radio(
                "Session Type",
                ["In-Memory", "Persistent"]
            )

        
        st.divider()

        st.subheader("Session Controls")

        if st.button("🗑️ Clear All Sessions"):
            with st.spinner("Clearing sessions..."):
                for session_id in list(st.session_state.session_manager.sessions.keys()):
                    asyncio.run(st.session_state.session_manager.clear_session(session_id))
                st.success("All sessions cleared!")
                st.rerun()


    if agent_type == "Basic":
        render_basic_agent(main_agent)
        
def render_basic_agent(agent):
    """Render the basic agent """
    name = st.text_input("Enter your name:")
    position = st.text_input("Position that you are applying for:")
    # job_

    if st.button("Generate Cover Letter"):
        st.write(f"Generating cover letter for {name} applying to {position}...")
    

def render_footer():
    st.divider()
    st.markdown("""
    ### 🎯 Session Capabilities Demonstrated
    
    1. **Basic Sessions**: In-memory vs persistent storage
    2. **Memory Operations**: get_items(), add_items(), pop_item(), clear_session()
    3. **Multi Sessions**: Multiple users, contexts, and agent handoffs
    
    **Key Benefits:**
    - Automatic conversation history management
    - Flexible session organization strategies
    - Memory manipulation for corrections and custom flows
    - Multi-agent conversation support
    """)

if __name__ == "__main__":
    main()
    render_footer()