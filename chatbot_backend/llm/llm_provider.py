from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from config.configures import config


def get_chat_model():
    """
    Get the appropriate chat model based on configuration
    
    Returns:
        Chat model instance (ChatGroq or ChatOpenAI)
        
    Raises:
        ValueError: If provider is unsupported or API key is missing
    """
    llm_config = config.llm
    
    if llm_config.provider == "groq":
        api_key = llm_config.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY not configured")
        return ChatGroq(
            api_key=api_key, 
            model=llm_config.groq_model, 
            temperature=llm_config.temperature
        )
    elif llm_config.provider == "openai":
        api_key = llm_config.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        return ChatOpenAI(
            model_name=llm_config.openai_model, 
            temperature=llm_config.temperature, 
            openai_api_key=api_key
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_config.provider}")
