/**
 * Pune Knowledge Base - Chat Interface
 */

class ChatInterface {
    constructor() {
        this.chatWidget = document.getElementById('chat-widget');
        this.chatToggle = document.getElementById('chat-toggle');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.chatSend = document.getElementById('chat-send');
        this.chatClose = document.getElementById('chat-close');
        
        this.messages = [];
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.chatToggle.addEventListener('click', () => this.toggle());
        this.chatClose.addEventListener('click', () => this.close());
        this.chatSend.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Load chat history from localStorage
        this.loadHistory();
        
        // Display welcome message
        this.addSystemMessage('Welcome to Pune Knowledge Base! Ask me anything about Pune - food, culture, attractions, and more.');
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.chatWidget.classList.add('active');
        this.isOpen = true;
        this.chatInput.focus();
    }
    
    close() {
        this.chatWidget.classList.remove('active');
        this.isOpen = false;
    }
    
    sendMessage() {
        const message = this.chatInput.value.trim();
        
        if (!message) {
            return;
        }
        
        // Add user message
        this.addUserMessage(message);
        this.chatInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to server
        this.getResponse(message);
    }
    
    addUserMessage(message) {
        this.addMessage(message, 'user');
    }
    
    addSystemMessage(message) {
        this.addMessage(message, 'system');
    }
    
    addMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${type}`;
        bubble.textContent = message;
        
        messageDiv.appendChild(bubble);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        // Store message
        this.messages.push({
            type: type,
            message: message,
            timestamp: new Date().toISOString()
        });
        
        // Save to localStorage
        this.saveHistory();
    }
    
    showTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message system';
        messageDiv.id = 'typing-indicator';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble system';
        bubble.innerHTML = '<span class="typing"><span></span><span></span><span></span></span>';
        
        messageDiv.appendChild(bubble);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    async getResponse(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get response');
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add system response
            if (data.response) {
                this.addSystemMessage(data.response);
            }
            
            // Add related articles if available
            if (data.articles && data.articles.length > 0) {
                this.addRelatedArticles(data.articles);
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.removeTypingIndicator();
            this.addSystemMessage('Sorry, I encountered an error. Please try again.');
        }
    }
    
    addRelatedArticles(articles) {
        const articlesDiv = document.createElement('div');
        articlesDiv.className = 'chat-message system';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble system';
        
        let html = '<strong>Related articles:</strong><ul style="margin: 0.5rem 0; padding-left: 1.5rem;">';
        articles.forEach(article => {
            html += `<li><a href="/article/${article.id}" target="_blank">${escapeHtml(article.title)}</a></li>`;
        });
        html += '</ul>';
        
        bubble.innerHTML = html;
        articlesDiv.appendChild(bubble);
        this.chatMessages.appendChild(articlesDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    saveHistory() {
        try {
            localStorage.setItem('chat_history', JSON.stringify(this.messages));
        } catch (error) {
            console.warn('Failed to save chat history:', error);
        }
    }
    
    loadHistory() {
        try {
            const history = localStorage.getItem('chat_history');
            if (history) {
                this.messages = JSON.parse(history);
                // Display last 10 messages
                const recentMessages = this.messages.slice(-10);
                recentMessages.forEach(msg => {
                    this.addMessage(msg.message, msg.type);
                });
            }
        } catch (error) {
            console.warn('Failed to load chat history:', error);
        }
    }
    
    clearHistory() {
        this.messages = [];
        this.chatMessages.innerHTML = '';
        localStorage.removeItem('chat_history');
        this.addSystemMessage('Chat history cleared.');
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.chatInterface = new ChatInterface();
});

// Add typing animation CSS
const style = document.createElement('style');
style.textContent = `
    .typing {
        display: inline-flex;
        gap: 4px;
    }
    
    .typing span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #999;
        animation: typing 1.4s infinite;
    }
    
    .typing span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            opacity: 0.5;
            transform: translateY(0);
        }
        30% {
            opacity: 1;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);
