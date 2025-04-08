// static/chat.js - Enhanced chat functionality with persistent history

// Chat history array
let chatHistory = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadChatHistory();
    setupEventListeners();
});

// Add document to knowledge base
async function addDocument(event) {
    event.preventDefault();
    const sourceInput = document.getElementById('source');
    const contentInput = document.getElementById('content');
    const feedbackMessage = document.getElementById('feedbackMessage');

    // Basic validation
    if (sourceInput.value.trim() === '' || contentInput.value.trim() === '') {
        feedbackMessage.textContent = 'Please fill in both source and content.';
        feedbackMessage.className = 'feedback-message error';
        return false;
    }

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: new FormData(event.target)
        });

        const result = await response.text();

        // Check if response contains success message
        if (response.ok) {
            feedbackMessage.textContent = 'Document added successfully!';
            feedbackMessage.className = 'feedback-message success';
            
            // Clear inputs
            sourceInput.value = '';
            contentInput.value = '';

            // Optionally reload documents list
            if (document.getElementById('viewDocs').classList.contains('active')) {
                loadDocuments();
            }
        } else {
            feedbackMessage.textContent = 'Failed to add document. Please try again.';
            feedbackMessage.className = 'feedback-message error';
        }
    } catch (error) {
        console.error('Error:', error);
        feedbackMessage.textContent = 'An error occurred while adding the document.';
        feedbackMessage.className = 'feedback-message error';
    }

    return false;
}

// Show selected tab
function showTab(tabId, tabElement) {
    // Clear any previous feedback messages
    const feedbackMessage = document.getElementById('feedbackMessage');
    feedbackMessage.textContent = '';
    feedbackMessage.className = 'feedback-message';

    // Existing tab switching logic
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    tabElement.classList.add('active');
    document.getElementById(tabId).classList.add('active');
    
    if (tabId === 'viewDocs') {
        loadDocuments();
    }
}

// Send a message to the chatbot
async function sendMessage() {
    const userQuestion = document.getElementById('userQuestion').value.trim();
    if (!userQuestion) return;
    
    // Add user message to chat
    addMessageToChat(userQuestion, 'user');
    document.getElementById('userQuestion').value = '';
    
    try {
        // Show typing indicator
        const typingDiv = addTypingIndicator();
        
        // Prepare chat history format for API
        const apiChatHistory = formatChatHistoryForAPI();
        
        // Call chat API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: userQuestion,
                chat_history: apiChatHistory
            })
        });
        
        // Remove typing indicator
        removeTypingIndicator(typingDiv);
        
        if (!response.ok) {
            throw new Error('Error getting response');
        }
        
        const data = await response.json();
        
        // Add bot response to chat
        addMessageToChat(data.answer, 'bot', data.sources);
        
    } catch (error) {
        console.error('Error:', error);
        // Remove typing indicator if still exists
        document.querySelectorAll('.typing-indicator').forEach(el => el.remove());
        addMessageToChat('Sorry, there was an error processing your request.', 'bot');
    }
}

// Format chat history for API request
function formatChatHistoryForAPI() {
    // Format the chat history for the API with proper role labels
    return chatHistory.map(msg => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content
    }));
}

// Add typing indicator
function addTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
    typingDiv.innerHTML = '<span>.</span><span>.</span><span>.</span>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
}

// Remove typing indicator
function removeTypingIndicator(element) {
    if (element && element.parentNode) {
        element.parentNode.removeChild(element);
    }
}

// Add a message to the chat display
function addMessageToChat(message, role, sources = []) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(role === 'user' ? 'user-message' : 'bot-message');
    
    // Add message content with proper formatting for new lines
    messageDiv.innerHTML = message.replace(/\n/g, '<br>');
    
    // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.classList.add('sources');
        sourcesDiv.innerHTML = '<strong>Sources:</strong> ' + 
            sources.map(s => s.source).join(', ');
        messageDiv.appendChild(sourcesDiv);
    }
    
    chatMessages.appendChild(messageDiv);
    
    // Auto scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to chat history
    chatHistory.push({
        role: role,
        content: message,
        sources: sources
    });
    
    // Save chat history to localStorage for persistence
    saveChatHistory();
}

// Save chat history to localStorage
function saveChatHistory() {
    try {
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
        console.log('Chat history saved to localStorage');
    } catch (e) {
        console.warn('Could not save chat history to localStorage', e);
    }
}

// Load documents from the API
async function loadDocuments() {
    const documentsList = document.getElementById('documentsList');
    documentsList.innerHTML = 'Loading...';
    
    try {
        // Search with an empty query to get all documents
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: "",
                max_results: 100
            })
        });
        
        if (!response.ok) {
            throw new Error('Error loading documents');
        }
        
        const documents = await response.json();
        
        if (documents.length === 0) {
            documentsList.innerHTML = '<p>No documents found. Add some economic data first.</p>';
            return;
        }
        
        // Display documents
        documentsList.innerHTML = '';
        documents.forEach(doc => {
            const docDiv = document.createElement('div');
            docDiv.classList.add('document-item');
            
            const sourceHeading = document.createElement('h3');
            sourceHeading.textContent = doc.source;
            docDiv.appendChild(sourceHeading);
            
            const content = document.createElement('p');
            content.textContent = doc.content.length > 200 ? 
                doc.content.substring(0, 200) + '...' : doc.content;
            docDiv.appendChild(content);
            
            documentsList.appendChild(docDiv);
        });
        
    } catch (error) {
        console.error('Error:', error);
        documentsList.innerHTML = '<p>Error loading documents: ' + error.message + '</p>';
    }
}

// Load chat history from localStorage
function loadChatHistory() {
    try {
        const savedHistory = localStorage.getItem('chatHistory');
        if (savedHistory) {
            chatHistory = JSON.parse(savedHistory);
            
            // Display loaded messages
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = ''; // Clear existing messages
            
            chatHistory.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message');
                messageDiv.classList.add(msg.role === 'user' ? 'user-message' : 'bot-message');
                
                // Add message content with proper formatting for new lines
                messageDiv.innerHTML = msg.content.replace(/\n/g, '<br>');
                
                // Add sources if available
                if (msg.sources && msg.sources.length > 0) {
                    const sourcesDiv = document.createElement('div');
                    sourcesDiv.classList.add('sources');
                    sourcesDiv.innerHTML = '<strong>Sources:</strong> ' + 
                        msg.sources.map(s => s.source).join(', ');
                    messageDiv.appendChild(sourcesDiv);
                }
                
                chatMessages.appendChild(messageDiv);
            });
            
            // Auto scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            console.log(`Loaded ${chatHistory.length} messages from localStorage`);
            return;
        }
    } catch (e) {
        console.warn('Could not load chat history from localStorage', e);
    }
    
    // Add welcome message if no history loaded
    addMessageToChat('Hello! I\'m your economics assistant. I can answer questions using my knowledge base or general knowledge. How can I help you today?', 'bot');
}

// Clear chat history
function clearChat() {
    // Clear chat display
    document.getElementById('chatMessages').innerHTML = '';
    
    // Clear chat history array
    chatHistory = [];
    
    // Clear localStorage
    localStorage.removeItem('chatHistory');
    
    // Also clear server-side session
    fetch('/api/session', {
        method: 'DELETE'
    }).then(() => {
        console.log('Server-side session cleared');
    }).catch(error => {
        console.error('Error clearing server-side session:', error);
    });
    
    // Add welcome message
    addMessageToChat('Chat history cleared. How can I help you today?', 'bot');
}

// Add event listeners
function setupEventListeners() {
    // Listen for Enter key in input field
    document.getElementById('userQuestion').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Add clear chat button functionality
    const clearChatButton = document.getElementById('clearChat');
    if (clearChatButton) {
        clearChatButton.addEventListener('click', function() {
            clearChat();
        });
    }
}