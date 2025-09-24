from langchain.prompts import ChatPromptTemplate
intent_detection_prompt = """
Bạn là một trợ lý AI giúp xác định ý định của khách hàng trong cửa hàng sách trực tuyến.       
Đoạn hội thoại: {user_message}
Dựa trên đoạn hội thoại, hãy phân loại ý định của họ thành một trong các loại sau:
1. order_book: Khách hàng muốn đặt mua sách hoặc đang trong quá trình cung cấp thông tin cá nhân.
2. search_book: Khách hàng muốn tìm kiếm thông tin về sách.
3. unknown: Không thể xác định ý định từ tin nhắn.  
Hãy trả về ý định dưới dạng một trong các từ khóa: "order_book", "search_book", hoặc "unknown". 
"""
INTENT_DETECTION_PROMPT = ChatPromptTemplate.from_template(intent_detection_prompt)
assistant_prompt = """
Bạn là trợ lý AI của một cửa hàng sách trực tuyến. 

## Đoạn hội thoại:
{user_message}
"""

ASSISTANT_PROMPT = ChatPromptTemplate.from_template(assistant_prompt)
extract_info_prompt = """
Khách hàng muốn đặt hàng. Hãy phân tích và trích xuất thông tin đơn hàng.

Đoạn hội thoại: {user_message}

Các thông tin cần trích xuất:
- book_title: Tên sách (nếu có)
- quantity: Số lượng sách (mặc định là 1 nếu không được đề cập)
- customer_name: Tên khách hàng (nếu có)
- phone: Số điện thoại (nếu có)
- address: Địa chỉ giao hàng (nếu có)

"""
EXTRACT_INFO_PROMPT = ChatPromptTemplate.from_template(extract_info_prompt)

order_assistant_prompt = """
Bạn là trợ lý AI chuyên hỗ trợ khách hàng đặt sách trực tuyến.
Dựa trên đoạn hội thoại và các thông tin hiện có, hãy xác định xem cần phải làm gì:
1. search: Tìm kiếm thêm thông tin về sách.
2. collect: Thu thập thông tin khách hàng.
3. update: Cập nhật thông tin đơn hàng hoặc thông tin khách hàng.
## Đoạn hội thoại:
{user_message}
## Các thông tin hiện có:
{order_info}
"""
ORDER_ASSISTANT_PROMPT = ChatPromptTemplate.from_template(order_assistant_prompt)