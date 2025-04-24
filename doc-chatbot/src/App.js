import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ChatBox from './components/ChatBox';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import './App.css';

const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
};

const AppContent = () => {
  const [sessionId, setSessionId] = useState(null);

  return (
    <div className="app">
      <ThemeToggle />
      <h1>Document Chatbot</h1>
      {!sessionId ? (
        <div className="upload-section">
          <h2>Upload a document to start chatting</h2>
          <FileUpload setSessionId={setSessionId} />
        </div>
      ) : (
        <div className="chat-section">
          <ChatBox sessionId={sessionId} />
          <button className="reset-btn" onClick={() => setSessionId(null)}>
            Upload New Document
          </button>
        </div>
      )}
    </div>
  );
};

const App = () => {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
};

export default App;