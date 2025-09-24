

from agent.langgraph import Agent

agent = Agent()

def chat_with_agent(user_text: str, user_id: str = None) -> str:
    """
    Chat with the agent and get a response
    
    Args:
        user_text: The input text from the user
        user_id: Optional user identifier for tracking purposes
        
    Returns:
        The response text from the agent
    """
    response = agent.run(user_text, user_id=user_id)
    return response