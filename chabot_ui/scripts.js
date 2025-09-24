// ===== Utility Functions =====
function generateUserId() {
    // Generate a simple short-term user ID
    const timestamp = Date.now().toString(36);
    const randomStr = Math.random().toString(36).substr(2, 5);
    return `user_${timestamp}_${randomStr}`;
}

// ===== Global Variables =====
// Use empty string for relative URLs since nginx will proxy to backend
let apiUrl = '';
let userId = generateUserId();
let isTyping = false;

// ===== DOM Elements =====
let messagesContainer, messageInput, chatForm, sendBtn, typingIndicator, settingsModal, apiUrlInput;

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', function () {
    // Initialize DOM elements after DOM is loaded
    messagesContainer = document.getElementById('messagesContainer');
    messageInput = document.getElementById('messageInput');
    chatForm = document.getElementById('chatForm');
    sendBtn = document.getElementById('sendBtn');
    typingIndicator = document.getElementById('typingIndicator');
    settingsModal = document.getElementById('settingsModal');
    apiUrlInput = document.getElementById('apiUrl');

    // Verify all elements are found
    if (!messagesContainer || !messageInput || !chatForm || !sendBtn || !typingIndicator || !settingsModal || !apiUrlInput) {
        console.error('Critical DOM elements not found!');
        return;
    }

    loadSettings();
    setupEventListeners();
    focusInput();
});

// ===== Event Listeners =====
function setupEventListeners() {
    // Chat form submission
    chatForm.addEventListener('submit', handleSendMessage);

    // Enter key handling
    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage(e);
        }
    });

    // Input validation
    messageInput.addEventListener('input', function () {
        const message = this.value.trim();
        sendBtn.disabled = message.length === 0 || isTyping;

        // Auto-resize textarea
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 100) + 'px';
    });

    // Modal click outside to close
    settingsModal.addEventListener('click', function (e) {
        if (e.target === settingsModal) {
            toggleSettings();
        }
    });

    // Escape key to close modal
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && settingsModal.classList.contains('show')) {
            toggleSettings();
        }
    });
}

// ===== Message Handling =====
async function handleSendMessage(e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message || isTyping) return;

    // Clear input and disable send button
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Add user message to chat
    addMessage(message, 'user');

    // Show typing indicator
    showTypingIndicator();

    try {
        // Send message to API
        const response = await sendMessageToAPI(message);

        // Hide typing indicator
        hideTypingIndicator();

        // Add bot response to chat
        if (response && response.response) {
            addMessage(response.response, 'bot', response.processing_time);
        } else {
            throw new Error('Invalid response format');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();

        // Show error message
        const errorMessage = 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau. 😔';
        addMessage(errorMessage, 'bot');
    }

    // Re-enable input
    sendBtn.disabled = false;
    focusInput();
}

async function sendMessageToAPI(message) {
    const requestData = {
        text: message,
        user_id: userId
    };

    const response = await fetch(`${apiUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    });

    json_response = await response.json();
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    console.log(json_response)
    return json_response;
}

// ===== UI Functions =====
function addMessage(text, sender, processingTime = null) {
    // Safety check for required elements
    if (!messagesContainer) {
        console.error('Messages container not found');
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'bot' ? '<i class="fas fa-book"></i>' : '<i class="fas fa-user"></i>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    // Format message content
    const formattedText = formatMessageText(text);
    bubbleDiv.innerHTML = formattedText;

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';

    let timeText = formatTime(new Date());
    if (processingTime && sender === 'bot') {
        timeText += ` • ${processingTime.toFixed(2)}s`;
    }
    timeDiv.textContent = timeText;

    contentDiv.appendChild(bubbleDiv);
    contentDiv.appendChild(timeDiv);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    // Insert message into container
    // Check if typing indicator is a child of messages container before inserting
    if (typingIndicator && messagesContainer.contains(typingIndicator)) {
        messagesContainer.insertBefore(messageDiv, typingIndicator);
    } else {
        messagesContainer.appendChild(messageDiv);
    }

    // Scroll to bottom
    scrollToBottom();

    // Add entrance animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';

    requestAnimationFrame(() => {
        messageDiv.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    });
}

function formatMessageText(text) {
    // Check for confirmation format
    const confirmRegex = /<confirm>([\s\S]*?)<\/confirm>/;
    const confirmMatch = text.match(confirmRegex);

    if (confirmMatch) {
        const confirmData = confirmMatch[1];
        const confirmCard = parseConfirmationData(confirmData);
        // Replace the confirmation block with the card
        text = text.replace(confirmRegex, confirmCard);
    }

    // Convert line breaks to HTML
    let formatted = text.replace(/\n/g, '<br>');

    // Convert markdown-like formatting
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    formatted = formatted.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');

    return formatted;
}

function parseConfirmationData(confirmData) {
    try {
        console.log('Raw confirmation data:', confirmData);
        console.log('Raw data type:', typeof confirmData);

        // Clean and normalize the string first
        let cleanedData = confirmData.trim();

        // Remove extra whitespace and newlines
        cleanedData = cleanedData.replace(/\s+/g, ' ');

        // Fix common JSON format issues
        cleanedData = cleanedData.replace(/\n/g, '').replace(/\r/g, '');

        // Try to fix malformed JSON by adding proper quotes and structure
        // Handle cases like: book_title: "sách của …address: "Hà nội"
        cleanedData = cleanedData.replace(/([a-zA-Z_]+):\s*"([^"]*?)…([a-zA-Z_]+):\s*"([^"]*?)"/g,
            '$1: "$2", $3: "$4"');

        // Add quotes around unquoted keys and values
        cleanedData = cleanedData.replace(/([a-zA-Z_]+):\s*([^",{}\n]+?)(?=[,}]|$)/g, '"$1": "$2"');

        // Handle quoted values that are already correct
        cleanedData = cleanedData.replace(/([a-zA-Z_]+):\s*"([^"]*?)"/g, '"$1": "$2"');

        // Ensure proper JSON structure
        if (!cleanedData.startsWith('{')) {
            cleanedData = '{' + cleanedData;
        }
        if (!cleanedData.endsWith('}')) {
            cleanedData = cleanedData + '}';
        }

        // Fix trailing commas
        cleanedData = cleanedData.replace(/,\s*}/g, '}');

        console.log('Cleaned confirmation data:', cleanedData);

        // Try to parse as JSON first
        let info;
        try {
            info = JSON.parse(cleanedData);
        } catch (jsonError) {
            console.warn('JSON parse failed, using regex extraction:', jsonError);

            // Fallback to regex extraction for malformed JSON
            info = {};

            // Extract values using more robust regex patterns
            const patterns = {
                book_id: /(?:book_id|id|ma_sach):\s*["{]?([^"{},:]*?)(?:["},]|$)/i,
                book_title: /(?:book_title|title|sach|book):\s*["{]?([^"{},:]*?)(?:["},]|$)/i,
                author: /(?:author|tac_gia|author_name):\s*["{]?([^"{},:]*?)(?:["},]|$)/i,
                category: /(?:category|danh_muc|the_loai):\s*["{]?([^"{},:]*?)(?:["},]|$)/i,
                quantity: /(?:quantity|so_luong|amount):\s*["{]?([^"{},:]*?)(?:["},]|$)/i,
                customer_name: /(?:customer_name|name|ten|ho_ten|fullname|user_name):\s*["{]?([^"{},:]*?)(?:["},]|$)/i,
                phone: /(?:phone|sdt|dien_thoai|mobile|telephone):\s*["{]?([^"{},:]*?)(?:["},]|$)/i,
                address: /(?:address|dia_chi|location):\s*["{]?([^"{},:]*?)(?:["},]|$)/i,
                price: /(?:price|cost|gia|thanh_tien):\s*["{]?([^"{},:]*?)(?:["},]|$)/i
            };

            for (const [key, pattern] of Object.entries(patterns)) {
                const match = confirmData.match(pattern);
                const value = match ? match[1].trim().replace(/["{},]/g, '') : '';
                info[key] = value;
                console.log(`Extracted ${key}:`, match ? `"${value}" (matched: "${match[0]}")` : 'NO MATCH');
            }
        }

        // Clean up extracted values
        Object.keys(info).forEach(key => {
            if (typeof info[key] === 'string') {
                // Remove unwanted characters and ellipsis
                info[key] = info[key].replace(/[…]/g, '').trim();
                // Remove quotes if they exist
                info[key] = info[key].replace(/^["']|["']$/g, '');
            }
        });

        console.log('Parsed confirmation info:', info);

        // Clean up invalid values
        Object.keys(info).forEach(key => {
            if (info[key] === '""' || info[key] === "''" || info[key] === 'None' || info[key] === 'null' || info[key] === 'undefined') {
                info[key] = '';
            }
        });

        // Debug: Show all parsed fields
        console.log('Final confirmation data:', {
            book_id: info.book_id,
            book_title: info.book_title,
            customer_name: info.customer_name || info.name || info.ten,
            phone: info.phone || info.sdt,
            address: info.address || info.dia_chi,
            quantity: info.quantity,
            price: info.price || info.gia,
            author: info.author,
            category: info.category
        });

        return createConfirmationCard(info);
    } catch (error) {
        console.error('Error parsing confirmation data:', error);
        return '<div class="error-card"><i class="fas fa-exclamation-triangle"></i> Không thể xử lý thông tin đặt hàng</div>';
    }
}

function createConfirmationCard(info) {
    const orderId = `order_${Date.now()}`;

    // Normalize field names - try multiple possible field names
    const customerName = info.customer_name || info.name || info.ten || info.ho_ten || info.fullname || info.user_name || '';
    const phoneNumber = info.phone || info.sdt || info.dien_thoai || info.mobile || info.telephone || '';
    const bookTitle = info.book_title || info.title || info.sach || info.book || '';
    const quantity = info.quantity || info.so_luong || info.amount || '1';
    const address = info.address || info.dia_chi || info.location || '';
    const price = info.price || info.gia || info.cost || info.thanh_tien || '';

    // Create normalized order object for API
    const normalizedOrder = {
        book_id: info.book_id || info.id || '',
        book_title: bookTitle,
        author: info.author || info.tac_gia || '',
        category: info.category || info.danh_muc || '',
        quantity: quantity,
        customer_name: customerName,
        phone: phoneNumber,
        address: address,
        price: price
    };

    console.log('Normalized order for button:', normalizedOrder);

    return `
        <div class="confirmation-card" data-order-id="${orderId}">
            <div class="card-header">
                <i class="fas fa-shopping-cart"></i>
                <h4>Xác nhận đặt hàng</h4>
            </div>
            <div class="card-body">
                <div class="order-details">
                    <div class="book-info">
                        <span class="book-label">📚</span>
                        <span class="book-title">${bookTitle || 'Chưa xác định'}</span>
                        <span class="quantity-badge">${quantity} cuốn</span>
                    </div>
                    <div class="customer-grid">
                        <div class="info-item">
                            <span class="info-label">👤</span>
                            <span class="info-text">${customerName || 'Chưa có thông tin'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">📞</span>
                            <span class="info-text">${phoneNumber || 'Chưa có số điện thoại'}</span>
                        </div>
                        <div class="info-item address-item">
                            <span class="info-label">📍</span>
                            <span class="info-text">${address || 'Chưa có địa chỉ'}</span>
                        </div>
                        ${price ? `
                        <div class="info-item price-item">
                            <span class="info-label">💰</span>
                            <span class="info-text">${price}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
            <div class="card-actions">
                <button class="btn-cancel" onclick="cancelOrder('${orderId}')">
                    <i class="fas fa-times"></i>
                    Hủy
                </button>
                <button class="btn-confirm" onclick="confirmOrder('${orderId}', ${JSON.stringify(normalizedOrder).replace(/"/g, '&quot;')})">
                    <i class="fas fa-check"></i>
                    Xác nhận
                </button>
            </div>
        </div>
    `;
}

function formatTime(date) {
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) { // Less than 1 minute
        return 'vừa xong';
    } else if (diff < 3600000) { // Less than 1 hour
        const minutes = Math.floor(diff / 60000);
        return `${minutes} phút trước`;
    } else if (diff < 86400000) { // Less than 1 day
        const hours = Math.floor(diff / 3600000);
        return `${hours} giờ trước`;
    } else {
        return date.toLocaleString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

function showTypingIndicator() {
    isTyping = true;
    typingIndicator.classList.add('show');
    scrollToBottom();
    sendBtn.disabled = true;
}

function hideTypingIndicator() {
    isTyping = false;
    typingIndicator.classList.remove('show');
    sendBtn.disabled = false;
}

function scrollToBottom() {
    if (!messagesContainer) return;

    requestAnimationFrame(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
}

function focusInput() {
    if (!messageInput) return;

    requestAnimationFrame(() => {
        messageInput.focus();
    });
}

// ===== Settings Functions =====
function toggleSettings() {
    settingsModal.classList.toggle('show');

    if (settingsModal.classList.contains('show')) {
        // Load current settings
        apiUrlInput.value = apiUrl;

        // Focus on first input
        setTimeout(() => apiUrlInput.focus(), 100);
    }
}

function saveSettings() {
    const newApiUrl = apiUrlInput.value.trim();

    // Validate API URL
    if (!newApiUrl) {
        alert('Vui lòng nhập API URL');
        return;
    }

    try {
        new URL(newApiUrl);
    } catch {
        alert('API URL không hợp lệ');
        return;
    }

    // Save settings
    apiUrl = newApiUrl;

    // Store in localStorage
    localStorage.setItem('chatbot_api_url', apiUrl);

    // Close modal
    toggleSettings();

    // Show success message
    showNotification('Cài đặt đã được lưu!', 'success');
}

function loadSettings() {
    const savedApiUrl = localStorage.getItem('chatbot_api_url');

    // If saved URL is old format (contains chatbot_backend or localhost), reset to empty
    if (savedApiUrl && !savedApiUrl.includes('chatbot_backend') && !savedApiUrl.includes('localhost')) {
        apiUrl = savedApiUrl;
    } else {
        // Use empty string for relative URLs (nginx proxy)
        apiUrl = '';
        // Clear old localStorage value
        localStorage.removeItem('chatbot_api_url');
    }
}

// ===== Order Management Functions =====
async function confirmOrder(orderId, orderInfo) {
    try {
        console.log('Confirming order:', orderId, orderInfo);

        // Disable buttons during processing
        const card = document.querySelector(`[data-order-id="${orderId}"]`);
        if (card) {
            const buttons = card.querySelectorAll('button');
            buttons.forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.7';
            });
        }

        // Prepare order data for API
        const orderData = {
            book_id: parseInt(orderInfo.book_id || orderInfo.id || '0') || 0,
            book_title: orderInfo.book_title || orderInfo.title || '',
            author: orderInfo.author || orderInfo.tac_gia || '',
            category: orderInfo.category || orderInfo.danh_muc || '',
            quantity: parseInt(orderInfo.quantity || '1') || 1,
            customer_name: orderInfo.customer_name || orderInfo.name || '',
            phone: orderInfo.phone || orderInfo.sdt || '',
            address: orderInfo.address || orderInfo.dia_chi || ''
        };

        // Validate required fields
        if (!orderData.book_id || orderData.book_id === 0) {
            console.error('Missing book_id in order data:', orderInfo);
            showNotification('Thiếu thông tin ID sách. Vui lòng thử lại.', 'error');
            // Re-enable buttons
            if (card) {
                const buttons = card.querySelectorAll('button');
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                });
            }
            return;
        }

        if (!orderData.customer_name || !orderData.phone || !orderData.address) {
            console.error('Missing required customer information:', orderData);
            showNotification('Thiếu thông tin khách hàng. Vui lòng thử lại.', 'error');
            // Re-enable buttons
            if (card) {
                const buttons = card.querySelectorAll('button');
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                });
            }
            return;
        }

        console.log('Sending order data to API:', orderData);

        // Send confirmation to API
        const response = await fetch(`${apiUrl}/api/v1/orders/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();
        console.log('API response:', result);

        // Handle response and update UI
        if (card) {
            if (response.ok && result.success) {
                const orderDetails = result.order_details;
                card.innerHTML = `
                    <div class="card-header success">
                        <i class="fas fa-check-circle"></i>
                        <h4>Đặt hàng thành công!</h4>
                    </div>
                    <div class="card-body">
                        <div class="success-content">
                            <p class="success-message">
                                <i class="fas fa-thumbs-up"></i>
                                ${result.message || 'Đơn hàng của bạn đã được xác nhận thành công!'}
                            </p>
                            ${orderDetails ? `
                            <div class="order-summary">
                                <p class="order-id">📋 Mã đơn hàng: <strong>#${orderDetails.order_id}</strong></p>
                                <p class="book-info">📚 ${orderDetails.book?.title} (${orderDetails.quantity} cuốn)</p>
                                <p class="total-amount">💰 Tổng tiền: <strong>${orderDetails.total_amount?.toLocaleString('vi-VN')} VNĐ</strong></p>
                                <p class="delivery-info">🚚 Giao hàng trong 2-3 ngày làm việc</p>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            } else {
                // Handle error response - restore card with retry option
                const errorMsg = result.detail?.message || result.message || 'Có lỗi xảy ra khi xác nhận đơn hàng';

                // Get the original order data from the card or button attributes
                const confirmBtn = card.querySelector('.btn-confirm');
                let originalOrderData = null;
                if (confirmBtn) {
                    try {
                        // Extract order data from onclick attribute
                        const onclickAttr = confirmBtn.getAttribute('onclick');
                        const dataMatch = onclickAttr.match(/confirmOrder\([^,]+,\s*({.*})\)/);
                        if (dataMatch) {
                            // Decode HTML entities and parse JSON
                            const decodedData = dataMatch[1].replace(/&quot;/g, '"');
                            originalOrderData = JSON.parse(decodedData);
                        }
                    } catch (e) {
                        console.error('Failed to extract original order data:', e);
                    }
                }

                // Show error message and restore confirmation card with retry button
                card.innerHTML = `
                    <div class="card-header error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h4>Lỗi xác nhận đơn hàng</h4>
                    </div>
                    <div class="card-body">
                        <p class="error-message">
                            <i class="fas fa-times-circle"></i>
                            ${errorMsg}
                        </p>
                        ${originalOrderData ? `
                        <div class="order-retry-info">
                            <p class="book-info">📚 ${originalOrderData.book_title}</p>
                            <p class="customer-info">👤 ${originalOrderData.customer_name}</p>
                        </div>
                        ` : ''}
                        <div class="retry-actions">
                            <button class="btn-cancel" onclick="cancelOrder('${orderId}')">
                                <i class="fas fa-times"></i>
                                Hủy
                            </button>
                            <button class="btn-retry" onclick="retryConfirmOrder('${orderId}', ${originalOrderData ? JSON.stringify(originalOrderData).replace(/"/g, '&quot;') : 'null'})">
                                <i class="fas fa-redo"></i>
                                Thử lại xác nhận
                            </button>
                        </div>
                    </div>
                `;
            }
        }

        // Show notification
        const isSuccess = response.ok && result.success;
        const message = isSuccess ? result.message : (result.detail?.message || result.message);
        showNotification(message || (isSuccess ? 'Đơn hàng đã được xác nhận!' : 'Có lỗi xảy ra'), isSuccess ? 'success' : 'error');

    } catch (error) {
        console.error('Error confirming order:', error);
        showNotification('Không thể kết nối đến server. Vui lòng thử lại.', 'error');

        // Re-enable buttons on error
        const card = document.querySelector(`[data-order-id="${orderId}"]`);
        if (card) {
            const buttons = card.querySelectorAll('button');
            buttons.forEach(btn => {
                btn.disabled = false;
                btn.style.opacity = '1';
            });
        }
    }
}

async function retryConfirmOrder(orderId, orderData) {
    console.log('Retrying order confirmation:', orderId, orderData);

    if (!orderData) {
        console.error('No order data available for retry');
        showNotification('Không có thông tin đơn hàng để thử lại. Vui lòng tạo đơn mới.', 'error');
        return;
    }

    // Simply call confirmOrder again with the same data
    await confirmOrder(orderId, orderData);
}

function cancelOrder(orderId) {
    console.log('Cancelling order:', orderId);

    const card = document.querySelector(`[data-order-id="${orderId}"]`);

    if (card) {
        // Simply update UI to show cancelled state - no API call needed
        card.innerHTML = `
            <div class="card-header cancelled">
                <i class="fas fa-times-circle"></i>
                <h4>Đơn hàng đã hủy</h4>
            </div>
            <div class="card-body">
                <p class="cancel-message">
                    <i class="fas fa-info-circle"></i>
                    Bạn đã hủy xác nhận đơn hàng này. Đơn hàng chưa được gửi đến hệ thống.
                </p>
            </div>
        `;

        showNotification('Đã hủy xác nhận đơn hàng', 'info');
    } else {
        console.error('Order card not found:', orderId);
        showNotification('Không tìm thấy đơn hàng để hủy', 'error');
    }
}

// ===== Utility Functions =====
function clearChat() {
    if (!messagesContainer) {
        console.error('Messages container not found');
        return;
    }

    const userMessages = messagesContainer.querySelectorAll('.message:not(.welcome-message)');

    if (userMessages.length === 0) {
        showNotification('Không có tin nhắn nào để xóa!', 'info');
        return;
    }

    if (confirm('Bạn có chắc muốn xóa toàn bộ lịch sử chat?')) {
        // Remove all messages except welcome message
        userMessages.forEach(message => {
            message.style.animation = 'slideOutDown 0.3s ease-in forwards';
            setTimeout(() => message.remove(), 300);
        });
        userId = generateUserId(); // Reset user ID for new session
        showNotification('Đã xóa lịch sử chat!', 'success');
        focusInput();
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        zIndex: '10000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        maxWidth: '300px',
        wordWrap: 'break-word'
    });

    // Set background color based on type
    const colors = {
        success: '#4ade80',
        error: '#ef4444',
        warning: '#fbbf24',
        info: '#3b82f6'
    };
    notification.style.background = colors[type] || colors.info;

    // Add to page
    document.body.appendChild(notification);

    // Animate in
    requestAnimationFrame(() => {
        notification.style.transform = 'translateX(0)';
    });

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ===== Animation Keyframes =====
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutDown {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(20px);
        }
    }
`;
document.head.appendChild(style);

// ===== Error Handling =====
window.addEventListener('error', function (e) {
    console.error('Global error:', e.error);
    showNotification('Đã có lỗi xảy ra!', 'error');
});

window.addEventListener('unhandledrejection', function (e) {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('Đã có lỗi xảy ra!', 'error');
});

// ===== Debug Functions (for testing) =====
function testConfirmationCard() {
    const testData = `{
        book_title: "Lập trình JavaScript ES6",
        quantity: "2",
        customer_name: "Nguyễn Văn A",
        phone: "0123456789",
        address: "123 Đường ABC, Quận 1, TP.HCM"
    }`;

    const testMessage = `Tôi đã thu thập đủ thông tin đặt hàng của bạn:

<confirm>${testData}</confirm>

Vui lòng kiểm tra và xác nhận thông tin đặt hàng.`;

    addMessage(testMessage, 'bot');
    console.log('Test confirmation card added to chat');
}

// Make test function available globally for debugging
window.testConfirmationCard = testConfirmationCard;

// ===== Service Worker Registration (Optional) =====
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        // You can register a service worker here for offline functionality
        // navigator.serviceWorker.register('/sw.js');
    });
}