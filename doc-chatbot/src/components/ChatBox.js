import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../context/ThemeContext';

function ChatBox({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { theme } = useTheme();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = currentMessage.trim();
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('question', userMessage);

      const response = await axios.post('http://localhost:8000/chat', formData);
      setMessages(prev => [...prev, { text: response.data.response, isUser: false }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        text: error.response?.data?.detail || 'Sorry, something went wrong. Please try again.',
        isUser: false,
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-history">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.isUser ? 'user' : 'bot'} ${message.isError ? 'error' : ''}`}
          >
            <div className={message.isUser ? 'user-message' : 'bot-message'}>
              {message.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <div className="bot-message loading">Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input">
        <input
          type="text"
          value={currentMessage}
          onChange={(e) => setCurrentMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !currentMessage.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatBox;