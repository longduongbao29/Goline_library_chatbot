// ===== Utility Functions =====
function generateUserId() {
    // Generate a simple short-term user ID
    const timestamp = Date.now().toString(36);
    const randomStr = Math.random().toString(36).substr(2, 5);
    return `user_${timestamp}_${randomStr}`;
}

// ===== Global Variables =====
let apiUrl = 'http://localhost:1234';
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

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
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
        // Parse the data from the string format
        const info = {};

        // Extract values using more flexible regex patterns
        const bookTitleMatch = confirmData.match(/book_title:\s*[{]?["']?(.*?)["']?[,}]?/);
        const quantityMatch = confirmData.match(/quantity:\s*[{]?["']?(.*?)["']?[,}]?/);
        const customerNameMatch = confirmData.match(/customer_name:\s*[{]?["']?(.*?)["']?[,}]?/);
        const phoneMatch = confirmData.match(/phone:\s*[{]?["']?(.*?)["']?[,}]?/);
        const addressMatch = confirmData.match(/address:\s*[{]?["']?(.*?)["']?[,}]?/);

        info.book_title = bookTitleMatch ? bookTitleMatch[1].trim() : '';
        info.quantity = quantityMatch ? quantityMatch[1].trim() : '';
        info.customer_name = customerNameMatch ? customerNameMatch[1].trim() : '';
        info.phone = phoneMatch ? phoneMatch[1].trim() : '';
        info.address = addressMatch ? addressMatch[1].trim() : '';

        // Clean up empty strings and special characters
        Object.keys(info).forEach(key => {
            if (info[key] === '""' || info[key] === "''" || info[key] === 'None' || info[key] === 'null') {
                info[key] = '';
            }
        });

        return createConfirmationCard(info);
    } catch (error) {
        console.error('Error parsing confirmation data:', error);
        return '<div class="error-card"><i class="fas fa-exclamation-triangle"></i> Không thể xử lý thông tin đặt hàng</div>';
    }
}

function createConfirmationCard(info) {
    const orderId = `order_${Date.now()}`;

    return `
        <div class="confirmation-card" data-order-id="${orderId}">
            <div class="card-header">
                <i class="fas fa-shopping-cart"></i>
                <h4>Xác nhận đặt hàng</h4>
            </div>
            <div class="card-body">
                <div class="order-details">
                    <div class="detail-row">
                        <span class="label">📚 Sách:</span>
                        <span class="value">${info.book_title || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">📦 SL:</span>
                        <span class="value">${info.quantity || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">👤 Tên:</span>
                        <span class="value">${info.customer_name || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">📞 SĐT:</span>
                        <span class="value">${info.phone || '-'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">📍 Địa chỉ:</span>
                        <span class="value">${info.address || '-'}</span>
                    </div>
                </div>
            </div>
            <div class="card-actions">
                <button class="btn-cancel" onclick="cancelOrder('${orderId}')">
                    <i class="fas fa-times"></i>
                    Hủy
                </button>
                <button class="btn-confirm" onclick="confirmOrder('${orderId}', ${JSON.stringify(info).replace(/"/g, '&quot;')})">
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

    if (savedApiUrl) {
        apiUrl = savedApiUrl;
    }
}

// ===== Order Management Functions =====
async function confirmOrder(orderId, orderInfo) {
    try {
        // Disable buttons during processing
        const card = document.querySelector(`[data-order-id="${orderId}"]`);
        if (card) {
            const buttons = card.querySelectorAll('button');
            buttons.forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.7';
            });
        }

        // Send confirmation to API
        const response = await fetch(`${apiUrl}/api/v1/confirm-order`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                order_id: orderId,
                user_id: userId,
                order_info: orderInfo,
                action: 'confirm'
            })
        });

        let result = { success: true, message: 'Đơn hàng đã được xác nhận thành công!' };

        if (response.ok) {
            result = await response.json();
        }

        // Update UI
        if (card) {
            if (result.success) {
                card.innerHTML = `
                    <div class="card-header success">
                        <i class="fas fa-check-circle"></i>
                        <h4>Đặt hàng thành công!</h4>
                    </div>
                    <div class="card-body">
                        <p class="success-message">${result.message || 'Đơn hàng của bạn đã được xác nhận và đang được xử lý.'}</p>
                        <p class="order-id">Mã đơn hàng: <strong>${orderId}</strong></p>
                    </div>
                `;
            } else {
                card.innerHTML = `
                    <div class="card-header error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h4>Lỗi xác nhận đơn hàng</h4>
                    </div>
                    <div class="card-body">
                        <p class="error-message">${result.message || 'Có lỗi xảy ra khi xác nhận đơn hàng.'}</p>
                    </div>
                `;
            }
        }

        // Show notification
        showNotification(result.message || 'Đơn hàng đã được xác nhận!', result.success ? 'success' : 'error');

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

async function cancelOrder(orderId) {
    try {
        const card = document.querySelector(`[data-order-id="${orderId}"]`);

        // Send cancel request to API
        const response = await fetch(`${apiUrl}/api/v1/confirm-order`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                order_id: orderId,
                user_id: userId,
                action: 'cancel'
            })
        });

        let result = { success: true, message: 'Đơn hàng đã được hủy.' };

        if (response.ok) {
            result = await response.json();
        }

        // Update UI
        if (card) {
            card.innerHTML = `
                <div class="card-header cancelled">
                    <i class="fas fa-times-circle"></i>
                    <h4>Đơn hàng đã hủy</h4>
                </div>
                <div class="card-body">
                    <p class="cancel-message">${result.message || 'Đơn hàng đã được hủy thành công.'}</p>
                </div>
            `;
        }

        showNotification('Đơn hàng đã được hủy', 'info');

    } catch (error) {
        console.error('Error cancelling order:', error);
        showNotification('Không thể hủy đơn hàng. Vui lòng thử lại.', 'error');
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