from langchain.prompts import ChatPromptTemplate
intent_detection_prompt = """
Bạn là một trợ lý AI giúp xác định ý định của khách hàng trong cửa hàng sách trực tuyến.       
Đoạn hội thoại: {user_message}
Dựa trên đoạn hội thoại, hãy phân loại ý định của họ thành một trong các loại sau:
1. order_book: Khách hàng muốn đặt mua sách hoặc đang trong quá trình cung cấp thông tin cá nhân.
2. search_book: Khách hàng muốn tìm kiếm thông tin về sách.
3. unknown: Không thể xác định ý định từ tin nhắn.  
Hãy trả về ý định dưới dạng một trong các từ khóa: "order_book", "search_book", hoặc "unknown". 

## Ví dụ 1:
Hội thoại: 
User: "Tôi muốn đặt mua sách Đắc Nhân Tâm"
Ý định: order_book

## Ví dụ 2:
Hội thoại: 
User: "Cho tôi xem những cuốn sách về lập trình Python"
Ý định: search_book

## Ví dụ 3:
Hội thoại: 
User: "Tôi tên Nguyễn Văn A, số điện thoại 0987654321"
Ý định: order_book

## Ví dụ 4:
Hội thoại: 
Asistant: "Cho mình xin địa chỉ của bạn nhé"
User: "Địa chỉ của tôi là 123 Nguyễn Trãi, Hà Nội"
Ý định: order_book

"""
INTENT_DETECTION_PROMPT = ChatPromptTemplate.from_template(intent_detection_prompt)
assistant_prompt = """
Bạn là trợ lý AI của một cửa hàng sách trực tuyến. 

## Đoạn hội thoại:
{user_message}
"""

ASSISTANT_PROMPT = ChatPromptTemplate.from_template(assistant_prompt)
extract_info_prompt = """
Bạn là trợ lý AI chuyên trích xuất thông tin đơn hàng từ hội thoại khách hàng.
Hãy phân tích và trích xuất các thông tin liên quan đến đơn hàng sách.

Dưới đây là một số ví dụ:

## Ví dụ 1:
Hội thoại: "Tôi muốn đặt mua sách Đắc Nhân Tâm 2 cuốn"
Thông tin trích xuất:
- book_title: "Đắc Nhân Tâm"
- quantity: 2
- customer_name: None
- phone: None
- address: None

## Ví dụ 2:
Hội thoại: "Chào shop, em tên Nguyễn Văn An, em muốn đặt sách Tôi Thấy Hoa Vàng Trên Cỏ Xanh 1 cuốn, số điện thoại 0987654321"
Thông tin trích xuất:
- book_title: "Tôi Thấy Hoa Vàng Trên Cỏ Xanh"
- quantity: 1
- customer_name: "Nguyễn Văn An"
- phone: "0987654321"
- address: None

## Ví dụ 3:
Hội thoại: "Tôi là Trần Thị Bình, tôi muốn đặt 3 cuốn sách Nhà Giả Kim, giao đến địa chỉ 123 Nguyễn Trãi, Hà Nội, số điện thoại 0912345678"
Thông tin trích xuất:
- book_title: "Nhà Giả Kim"
- quantity: 3
- customer_name: "Trần Thị Bình"
- phone: "0912345678"
- address: "123 Nguyễn Trãi, Hà Nội"

---

Bây giờ hãy trích xuất thông tin từ hội thoại sau:
Đoạn hội thoại: {user_message}

Các thông tin cần trích xuất:
- book_title: Tên sách (nếu có, để None nếu không có)
- quantity: Số lượng sách (mặc định là 1 nếu không được đề cập)
- customer_name: Tên khách hàng (nếu có, để None nếu không có)
- phone: Số điện thoại (nếu có, để None nếu không có)
- address: Địa chỉ giao hàng (nếu có, để None nếu không có)

Lưu ý:
- Nếu có nhiều cuốn sách được đề cập, hãy gộp tên sách lại và cộng số lượng
- Số điện thoại thường bắt đầu bằng 0 và có 10-11 chữ số
- Tên sách có thể được viết theo nhiều cách khác nhau
- Nếu không có thông tin gì được đề cập thì để None
"""
EXTRACT_INFO_PROMPT = ChatPromptTemplate.from_template(extract_info_prompt)

order_assistant_prompt = """
Bạn là trợ lý AI chuyên hỗ trợ khách hàng đặt sách trực tuyến.
Dựa trên đoạn hội thoại và các thông tin hiện có, hãy xác định xem cần phải làm gì.
## Đoạn hội thoại:
{user_message}
## Các thông tin hiện có:
{order_info}
"""
ORDER_ASSISTANT_PROMPT = ChatPromptTemplate.from_template(order_assistant_prompt)