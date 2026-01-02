import asyncio
import io
import os
from pathlib import Path

import PyPDF2
import streamlit as st
from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(
	page_title="Cover Letter Generator",
	page_icon="📝",
	layout="centered",
	initial_sidebar_state="expanded",
)


# Session type
SESSION_TYPE = "persistent"


def load_examples(
	folder: str,
	exts: tuple[str, ...] = (".pdf",),
	max_chars_per_file: int = 2500,
	max_total_chars: int = 10000,
) -> str:
	"""Load example cover letters/resumes from the examples folder."""

	p = Path(folder)
	if not p.exists() or not p.is_dir():
		return ""

	texts: list[str] = []
	total = 0

	for f in sorted(p.iterdir()):
		if f.suffix.lower() not in exts:
			continue
		try:
			if f.suffix.lower() == ".pdf":
				reader = PyPDF2.PdfReader(str(f))
				pages_text = []
				for page in reader.pages:
					pages_text.append(page.extract_text() or "")
				t = "\n".join(pages_text).strip()
			else:
				t = f.read_text(encoding="utf-8").strip()
		except Exception:
			continue

		if not t:
			continue
		if len(t) > max_chars_per_file:
			t = t[:max_chars_per_file] + "\n\n...[truncated]"
		if total + len(t) > max_total_chars:
			break

		texts.append(f"---\nFilename: {f.name}\n\n{t}")
		total += len(t)

	return "\n\n".join(texts)


def initialize_main_agent(examples_dir: str | None) -> Agent:
	"""Initialize our main agent."""

	base_instructions = """
		You are a helping assistant for writing cover letters based on the user inputted name, email, linkedin job description, as well as some presupplied example cover letters.

		Remember previous conversation context and reference it when relevant. Use the resume that the user has provided to create a well tailored professional resume.
		Be friendly and professional.
		"""

	examples_text = load_examples(examples_dir) if examples_dir else ""
	if examples_text:
		base_instructions += (
			"\n\nEXAMPLE COVER LETTERS (use these for style/formatting reference):\n\n"
			+ examples_text
		)

	return Agent(
		name="Cover Letter Agent",
		instructions=base_instructions,
	)


def initialize_agent() -> Agent:
	"""Initialize our Cover Letter Agent."""

	return initialize_main_agent(examples_dir="examples")


class SessionManager:
	def __init__(self):
		self.sessions: dict[str, SQLiteSession] = {}

	def get_session(self, session_id: str, db_file: str = "cover_letter.db") -> SQLiteSession:
		"""Get or create a session."""

		if session_id not in self.sessions:
			self.sessions[session_id] = SQLiteSession(session_id, db_file)
		return self.sessions[session_id]

	async def clear_session(self, session_id: str) -> None:
		"""Clear a specific session."""

		if session_id in self.sessions:
			await self.sessions[session_id].clear_session()
			del self.sessions[session_id]

	async def get_session_items(self, session_id: str, limit: int | None = None):
		"""Get conversation items from a session."""

		if session_id in self.sessions:
			return await self.sessions[session_id].get_items(limit=limit)
		return []


if "session_manager" not in st.session_state:
	st.session_state.session_manager = SessionManager()


def render_basic_agent(agent: Agent) -> None:
	"""Render the basic agent."""

	name = st.text_input("Enter your name:")
	position = st.text_input("Position that you are applying for:")
	job_description = st.text_area("Job description from website:")
	current_resume = st.file_uploader("Upload Resume", type=["pdf"])
	skills = st.text_input("Key skills (comma-separated, optional):")
	additional_info = st.text_area("Additional details (optional):")

	first_page_text = ""
	if current_resume is not None:
		bytes_io = io.BytesIO(current_resume.getvalue())
		try:
			pdf_reader = PyPDF2.PdfReader(bytes_io)
			st.success(f"Successfully uploaded {current_resume.name}")
			st.write(f"The PDF has {len(pdf_reader.pages)} pages.")
			if pdf_reader.pages:
				first_page_text = pdf_reader.pages[0].extract_text() or ""
		except Exception:
			st.warning("Uploaded PDF could not be read/extracted.")

	generate = st.button("Generate Cover Letter")

	if generate and name and position and job_description and current_resume:
		# Ensure OpenAI key exists (either via sidebar input or .env)
		if not os.getenv("OPENAI_API_KEY"):
			st.error("Missing OpenAI API key. Add it in the sidebar (or in .env as OPENAI_API_KEY).")
			return

		user_input = (
			f"Name: {name}\n"
			f"Position: {position}\n\n"
			f"Job Description:\n{job_description}\n\n"
		)

		user_input += (
			f"Resume Text (first page):\n{first_page_text if first_page_text else '<could not extract>'}\n\n"
		)

		if skills:
			user_input += f"Skills: {skills}\n\n"
		if additional_info:
			user_input += f"Additional Info:\n{additional_info}\n\n"

		with st.spinner(f"Generating cover letter for {name} applying to {position}..."):
			session = st.session_state.session_manager.get_session(SESSION_TYPE, "cover_letter.db")
			result = asyncio.run(Runner.run(agent, user_input, session=session))
			st.success("Message sent!")
			st.write(f"**Assistant:** {result.final_output}")
	elif generate:
		st.info("❌Please provide input for the above fields❌")

	if st.button("📧 Show Previous Cover Letters", key="show_persistent"):
		items = asyncio.run(st.session_state.session_manager.get_session_items(SESSION_TYPE))
		assistant_items = [item for item in items if item.get("role") == "assistant"]

		if assistant_items:
			st.write("**Generated Cover Letters:**")
			for item in assistant_items:
				st.write(item["content"][0]["text"])
				st.divider()
		else:
			st.info("No generated cover letters yet.")


def render_footer() -> None:
	st.divider()
	st.markdown(
		"""
	### Generate a starter cover letter easily

	The agents are shown as below, choose the one that fits best for you.

	1. **Basic**: Basic agent with in-memory and persistant sessions
		- Input: name, position, job description, and resume

	"""
	)


def main() -> None:
	st.title("Cover Letter Generator")
	st.write("Generate Professional Cover Letters Easily")

	with st.sidebar:
		st.header("⚙️ Session Configuration")

		openai_key = st.text_input(
			"OpenAI API key",
			type="password",
			value=st.session_state.get("openai_api_key", ""),
			help="Stored only for this browser session; also supports .env via OPENAI_API_KEY.",
		)
		if openai_key:
			st.session_state.openai_api_key = openai_key
			os.environ["OPENAI_API_KEY"] = openai_key

		agent_type = st.selectbox("Select Agent Type", ["Basic"])
		st.divider()
		st.subheader("Session Controls")
		if st.button("🗑️ Clear All Sessions"):
			with st.spinner("Clearing sessions..."):
				for session_id in list(st.session_state.session_manager.sessions.keys()):
					asyncio.run(st.session_state.session_manager.clear_session(session_id))
			st.success("All sessions cleared!")
			st.rerun()

	# initialize agent after we potentially set OPENAI_API_KEY
	main_agent = initialize_agent()

	if agent_type == "Basic":
		render_basic_agent(main_agent)


if __name__ == "__main__":
	main()
	render_footer()

