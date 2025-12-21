from agents import Agent
from pathlib import Path
import PyPDF2

def load_examples(folder, exts=(".pdf"), max_chars_per_file: int = 2500, max_total_chars: int = 10000):
    p = Path(folder)
    if not p.exists() or not p.is_dir():
        return ""
    texts = []
    total = 0
    for f in sorted(p.iterdir()):
        if f.suffix.lower() not in exts:
            continue
        try:
            if f.suffix.lower() == ".pdf":
                # read PDF text
                reader = PyPDF2.PdfReader(str(f))
                pages_text = []
                for page in reader.pages:
                    text = page.extract_text() or ""
                    pages_text.append(text)
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

def initialize_main_agent(examples_dir):
    """Initialize our main agent"""
    base_instructions= """
        You are a helping assistant for writing cover letters based on the user inputted name, email, linkedin job description, as well as some presupplied example cover letters.

        Remember previous conversation context and reference it when relevant. Use the resume that the user has provided to create a well tailored professional resume.
        Be friendly and professional.
        """
    
    examples_text = ""
    if examples_dir:
        examples_text = load_examples(examples_dir)

    if examples_text:
        base_instructions += "\n\nEXAMPLE COVER LETTERS (use these for style/formatting reference):\n\n" + examples_text
    main_agent = Agent(
        name="Cover Letter Agent",
        instructions=base_instructions
    )
    return main_agent