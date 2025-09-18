document.addEventListener('DOMContentLoaded', () => {
    // Speech Synthesis Configuration
    const synth = window.speechSynthesis;
    let voices = [];
    let isSpeaking = false;

    // DOM Elements
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.querySelector('.typing-indicator');

    // Initialize speech voices
    function loadVoices() {
        voices = synth.getVoices();
        // Optional: Set preferred voice
        // return voices.find(voice => voice.name.includes('Google'));
    }

    // Enhanced message creation with sanitization
    function createMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        // Safe HTML formatting
        if (typeof content === 'string') {
            const parser = new DOMParser();
            const sanitized = parser.parseFromString(content, 'text/html').body.textContent || '';
            messageDiv.innerHTML = sanitized
                .replace(/\n/g, '<br>')
                .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        } else {
            messageDiv.appendChild(content);
        }
        
        return messageDiv;
    }

    // Enhanced message handling
    function appendMessage(content, isUser = false) {
        const message = createMessage(content, isUser);
        chatBox.appendChild(message);
        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });
    }

    // Speech synthesis handler
    function speak(text) {
        if (!synth || isSpeaking) return;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = voices[0]; // Use first available voice
        utterance.pitch = 1;
        utterance.rate = 1;

        utterance.onstart = () => {
            isSpeaking = true;
            chatBox.classList.add('speaking');
        };

        utterance.onend = () => {
            isSpeaking = false;
            chatBox.classList.remove('speaking');
        };

        synth.speak(utterance);
    }

    // API request handler with timeout
    async function fetchBotResponse(message) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        try {
            const response = await fetch(`/get_response/?message=${encodeURIComponent(message)}`, {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) throw new Error('API response error');
            return await response.json();
        } catch (error) {
            throw new Error(error.message || 'Failed to fetch response');
        }
    }

    // Main message handler
    async function handleSend() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message
        appendMessage(message, true);
        userInput.value = '';
        sendBtn.disabled = true;

        // Show typing indicator
        typingIndicator.style.display = 'flex';

        try {
            const { response } = await fetchBotResponse(message);
            
            // Handle search results
            if (response.includes('🔍')) {
                const searchUrl = response.match(/https?:\/\/[^\s]+/)?.[0];
                if (searchUrl) {
                    const searchContent = document.createElement('div');
                    searchContent.innerHTML = `
                        ${response.split('\n')[0]}<br>
                        <a href="${searchUrl}" class="search-link" target="_blank" rel="noopener">
                            Open Search Results
                        </a>
                    `;
                    appendMessage(searchContent);
                }
            } else {
                appendMessage(response);
                speak(response); // Speak bot response
            }
        } catch (error) {
            appendMessage(`⚠️ Error: ${error.message}`);
        } finally {
            typingIndicator.style.display = 'none';
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    // Quick reply handler
    document.querySelectorAll('.quick-reply').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.add('active');
            setTimeout(() => btn.classList.remove('active'), 200);
            userInput.value = btn.textContent;
            handleSend();
        });
    });

    // Input handlers
    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    // Initialize voices when available
    synth.onvoiceschanged = loadVoices;

    // Initial setup
    loadVoices();
    userInput.focus();
});