# Cover_Letter_Generator

## Usage

**Quick Start**
- **Install**: Run `pip install -r requirements.txt`.
- **Run**: Start the UI with `streamlit run app.py`.
- **Env**: Add any API keys or config to a `.env` file (the app calls `load_dotenv()`).

**Inputs**
- **Name**: Your full name.
- **Position**: Job title you're applying for.
- **Job Description**: Paste the job posting or description.
- **Resume**: Upload a PDF (first page text is extracted).
- **Skills**: Comma-separated key skills (optional).
- **Additional Info**: Anything extra to include (optional).

**How To Use**
- Open the app with:

```bash
streamlit run app.py
```

- Fill `Name`, `Position`, and `Job Description`.
- Upload your resume PDF and enter `Skills` / `Additional Info` if desired.
- Click **Generate Cover Letter**. The generated letter appears under **Assistant**.
- Click **Show Previous Cover Letters** to view saved/persistent outputs.
- Use the sidebar control **Clear All Sessions** to clear stored sessions.

**Example**
- Provide:
	- Name: Jane Doe
	- Position: Product Manager
	- Job Description: (paste posting text)
	- Resume: upload `Jane_Doe_Resume.pdf`
- Click `Generate Cover Letter` → the app displays a tailored cover letter in the UI.

**Behavior & Notes**
- The app extracts text from the first page of the uploaded PDF to help tailor the letter.
- Generation is performed by the configured agent (`agent_config.py` / `examples/`).
- Sessions are persisted in `cover_letter.db` (persistent session type).

**Troubleshooting**
- If the resume text isn’t extracted, ensure the PDF has selectable text (not scanned images).
- If Streamlit fails to run, confirm `streamlit` is installed and use `streamlit --version`.
- For missing API keys, add them to `.env` and restart the app.

---