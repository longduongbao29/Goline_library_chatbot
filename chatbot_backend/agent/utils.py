from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

def format_message(messages, last_n=10):
    messages = messages[-last_n*2:]
    formatted = ""
    for message in messages:
        role = "unknown"
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, SystemMessage):
            role = "system"
        elif isinstance(message, ToolMessage):
            role = "tool"
        content = message.content
        formatted += f"{role.capitalize()}: {content}\n"
    return formatted