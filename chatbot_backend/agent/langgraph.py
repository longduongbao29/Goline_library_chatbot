
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode, tools_condition

from llm.llm_provider import get_chat_model
from agent.state import State
from agent.tools import search_book, search_book_func
from agent.prompts import INTENT_DETECTION_PROMPT, ASSISTANT_PROMPT, EXTRACT_INFO_PROMPT, ORDER_ASSISTANT_PROMPT
from agent.structured_output import IntentDetection, OrderInfo, OrderIntent
from agent.utils import format_message
from utils.logger import Logger
logger = Logger(__name__).get_logger()

class Agent:
    def __init__(self):
        self.llm = get_chat_model()
        self.memory = InMemorySaver()
        self.graph = self.build_graph()
   
    def detect_intent(self, state) :
        logger.debug("\ndetect_intent node\n")
        structured_llm = self.llm.with_structured_output(IntentDetection)
        
        messages = format_message(state['messages'])
        
        chain = INTENT_DETECTION_PROMPT | structured_llm
        response: IntentDetection = chain.invoke({"user_message": messages})
        return response.intent
    
    def qa_assistant(self, state) :
        logger.debug("\nqa_assistant node\n")
        
        llm_with_tools = self.llm.bind_tools([search_book])
        messages = format_message(state['messages'])
        chain = ASSISTANT_PROMPT | llm_with_tools
        response = chain.invoke({"user_message": messages})
        return {"messages": [response]}

    def extract_info(self, state) :
        logger.debug("\nextract_info node\n")
        messages = format_message(state['messages'])
        structured_llm = self.llm.with_structured_output(OrderInfo)
        chain = EXTRACT_INFO_PROMPT | structured_llm
        response: OrderInfo = chain.invoke({"user_message": messages})
        state["order_info"] = response.dict()
        return state
    def order_assistant(self, state) :
        logger.debug("\norder_assistant node\n")
        return state
    def order_assistant_intent(self, state) :
        logger.debug("\norder_assistant node\n")
        messages = format_message(state['messages'])
        structured_llm = self.llm.with_structured_output(OrderIntent)
        chain = ORDER_ASSISTANT_PROMPT | structured_llm
        response: OrderIntent = chain.invoke({"user_message": messages, "order_info": state["order_info"]})
        return response.action
    def search_book_info(self, state):
        logger.debug("\nsearch_book_info node\n")
        # Implement the logic to search for book information
        search = search_book_func(state["order_info"].get("book_title", ""))
        book = search["books"][0] if search and search.get("books") else None
        if book:
            state["order_info"]["book_id"] = book.get("id")
            state["order_info"]["author"] = book.get("author")
            state["order_info"]["genre"] = book.get("genre")
            state["order_info"]["category"] = book.get("category")
            state["order_info"]["availability"] = book.get("availability")
            state["order_info"]["book_title_in_db"] = book.get("title")
        else:
            state["order_info"]["book_id"] = None
            state["order_info"]["author"] = None
            state["order_info"]["genre"] = None
            state["order_info"]["category"] = None
        return state
    def check_missing_info(self, state) :
        logger.debug("\ncheck_missing_info node\n")
        missing_info = []
        for field in state["order_info"]:
            if state["order_info"][field] is None or state["order_info"][field] == "" or state["order_info"][field] == "None":
                missing_info.append(field)
        search_fields = ["book_id", "author", "genre","category", "book_title_in_db"]
        personal_info_fields = ["customer_name", "phone", "address", "quantity"]
        if any(field in missing_info for field in search_fields):
            return "search_book_info"
        if any(field in missing_info for field in personal_info_fields):
            return "follow_up_question"
        return "confirm_order"

    def follow_up_question(self, state) :
        logger.debug("\nfollow_up_question node\n")
        missing_info = []
        for field in state["order_info"]:
            if state["order_info"][field] is None or state["order_info"][field] == "" or state["order_info"][field] == "None":
                missing_info.append(field)
        book_title = state["order_info"].get("book_title", "")
        book_title_in_db = state["order_info"].get("book_title_in_db", "")
        if book_title and book_title_in_db:
            if book_title != book_title_in_db:
                message = AIMessage(content=f"Có phải ý bạn là cuốn '{book_title_in_db}' không?")
                return {"messages": [message]}
        question_map = {
            "book_title": "Bạn muốn đặt mua cuốn sách nào?",
            "quantity": "Bạn muốn đặt bao nhiêu cuốn?",
            "customer_name": "Bạn có thể cho tôi biết tên của bạn được không?",
            "phone": "Số điện thoại của bạn là gì?",
            "address": "Bạn có thể cung cấp địa chỉ giao hàng được không?"
        }

        message = AIMessage(content=question_map[missing_info[0]])
        return {"messages": [message]}
    
    def confirm_order(self, state):
        logger.debug("\nconfirm_order node\n")
        info = state["order_info"]
        confirm=f"""
        <confirm>{{
        book_title: "{info.get("book_title", "")}",
        quantity: "{info.get("quantity", "")}",
        customer_name: "{info.get("customer_name", "")}",
        phone: "{info.get("phone", "")}",
        address: "{info.get("address", "")}"
                    }}</confirm>"""
        message = AIMessage(content=confirm)
        return {"messages": [message]}
    def build_graph(self):
        graph = StateGraph(State)
        graph.add_node("qa_assistant", self.qa_assistant)
        graph.add_node("extract_info", self.extract_info)
        graph.add_node("search_book_info", self.search_book_info)
        graph.add_node("follow_up_question", self.follow_up_question)
        graph.add_node("order_assistant", self.order_assistant)
        tool_node = ToolNode(tools=[search_book])
        graph.add_node("tools", tool_node)
        graph.add_node("confirm_order", self.confirm_order)
        graph.add_conditional_edges(START,self.detect_intent, {
            "order_book": "order_assistant",
            "search_book": "qa_assistant",
            "unknown": "qa_assistant"
        })
        graph.add_conditional_edges("qa_assistant", tools_condition,)
        graph.add_edge("tools", "qa_assistant")
        
        graph.add_conditional_edges("order_assistant", self.order_assistant_intent,{
            "search": "search_book_info",
            "collect": "extract_info",
            "update": "extract_info"
        })
        graph.add_conditional_edges("extract_info", self.check_missing_info, {
            "follow_up_question": "follow_up_question",
            "search_book_info": "order_assistant",
            "confirm_order": "confirm_order"
        })
        graph.add_conditional_edges("search_book_info", self.check_missing_info, {
            "follow_up_question": "follow_up_question",
            "search_book_info": "search_book_info",
            "confirm_order": "confirm_order"
        })
        graph.add_edge("confirm_order", END)
        graph.add_edge("follow_up_question", END)
        return graph.compile(checkpointer = self.memory)
    def run(self, user_input, user_id):
        config = {"configurable": {"thread_id": user_id}}
        message = {"role": "user", "content": user_input}
        order_info = {
            "book_title": None,
            "quantity": 1,
            "customer_name": None,
            "phone": None,
            "address": None,
            "book_id": None,
            "author": None,
            "category": None,
        }
        response = self.graph.invoke({"messages": [message], "order_info": order_info}, config)
        last_message = response.get("messages", [])[-1] if response.get("messages") else None
       
        if last_message:
            if hasattr(last_message, 'content'):
                return last_message.content
            elif isinstance(last_message, dict) and 'content' in last_message:
                return last_message['content']
        return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này."