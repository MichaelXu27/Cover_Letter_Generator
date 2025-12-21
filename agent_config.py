from agents import Agent

def initialize_main_agent():
    """Initialize our main agent"""
    main_agent = Agent(
        name="Cover Letter Agent",
        instructions="""
        You are a helping assistant for writing cover letters based on the user inputted name, email, linkedin job description, as well as some presupplied example cover letters.

        Remember previous conversation context and reference it when relevant. The user may as you to refine some aspects so just be aware of that. 
        Be friendly and professional.
        """
    )
    return main_agent