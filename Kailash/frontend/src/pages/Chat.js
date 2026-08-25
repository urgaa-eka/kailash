import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageCircle, Send, Trash2, RefreshCw, Plus, 
  Loader2, AlertCircle, CheckCircle, Sparkles 
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import './Chat.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Chat = () => {
  const { token, user } = useAuthStore();
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [error, setError] = useState(null);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [currentDepartment, setCurrentDepartment] = useState(null);
  
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load conversation messages when selected
  useEffect(() => {
    if (currentConversation) {
      loadConversationMessages(currentConversation.id);
    }
  }, [currentConversation]);

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true);
      const response = await fetch(`${BACKEND_URL}/api/conversations?limit=50`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Failed to load conversations');
      
      const data = await response.json();
      setConversations(data.conversations || []);
      
      // Auto-select first conversation if available
      if (data.conversations && data.conversations.length > 0 && !currentConversation) {
        setCurrentConversation(data.conversations[0]);
      }
    } catch (err) {
      console.error('Error loading conversations:', err);
      setError('Failed to load conversations');
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const loadConversationMessages = async (conversationId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Failed to load messages');
      
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Error loading messages:', err);
      setError('Failed to load messages');
    }
  };

  const createNewConversation = async (firstMessage) => {
    // Create a new conversation by storing it in MongoDB
    const newConvId = Date.now().toString();
    const newConv = {
      id: newConvId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      message_count: 1,
      preview: firstMessage.substring(0, 100)
    };
    
    setCurrentConversation(newConv);
    setConversations([newConv, ...conversations]);
    setMessages([]);
    
    return newConvId;
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);
    setIsLoading(true);
    setStreamingMessage('');
    setCurrentDepartment(null);

    // Add user message to UI
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, newUserMessage]);

    // Create new conversation if none selected
    let conversationId = currentConversation?.id;
    if (!conversationId) {
      conversationId = await createNewConversation(userMessage);
    }

    try {
      // Abort any ongoing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();

      // Call GANESHA orchestrator with SSE streaming
      const response = await fetch(`${BACKEND_URL}/api/ganesha/orchestrate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_message: userMessage,
          conversation_history: messages.slice(-10).map(m => ({
            role: m.role,
            content: m.content
          }))
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.status}`);
      }

      // Handle SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.substring(6));
              
              // Handle different event types
              if (eventData.type === 'ganesha_thinking' || eventData.type === 'message') {
                const content = eventData.content || eventData.text || '';
                fullResponse += content;
                setStreamingMessage(fullResponse);
              } else if (eventData.type === 'department_routing') {
                setCurrentDepartment(eventData.department);
              } else if (eventData.type === 'error') {
                throw new Error(eventData.message || 'Stream error');
              }
            } catch (parseErr) {
              console.error('Error parsing SSE event:', parseErr);
            }
          }
        }
      }

      // Add assistant message to chat
      const assistantMessage = {
        role: 'assistant',
        content: fullResponse || 'Response received.',
        timestamp: new Date().toISOString(),
        department: currentDepartment
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setStreamingMessage('');
      
      // Reload conversations to update preview
      await loadConversations();
      
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Request aborted');
      } else {
        console.error('Error sending message:', err);
        setError('Failed to send message. Please try again.');
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleDeleteConversation = async (conversationId) => {
    if (!window.confirm('Delete this conversation?')) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete conversation');
      
      // Remove from list
      const updatedConversations = conversations.filter(c => c.id !== conversationId);
      setConversations(updatedConversations);
      
      // Clear current conversation if it was deleted
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(updatedConversations[0] || null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Error deleting conversation:', err);
      setError('Failed to delete conversation');
    }
  };

  const handleClearConversation = async () => {
    if (!currentConversation || !window.confirm('Clear all messages in this conversation?')) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/conversations/${currentConversation.id}/clear`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to clear conversation');
      
      setMessages([]);
      await loadConversations();
    } catch (err) {
      console.error('Error clearing conversation:', err);
      setError('Failed to clear conversation');
    }
  };

  const handleNewChat = () => {
    setCurrentConversation(null);
    setMessages([]);
    setStreamingMessage('');
    setCurrentDepartment(null);
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
      return date.toLocaleDateString();
    } catch {
      return '';
    }
  };

  return (
    <div className="chat-container">
      {/* Sidebar */}
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <h2>
            <MessageCircle size={20} />
            Conversations
          </h2>
          <button 
            className="btn-new-chat" 
            onClick={handleNewChat}
            title="New conversation"
          >
            <Plus size={18} />
          </button>
        </div>

        <div className="conversations-list">
          {isLoadingConversations ? (
            <div className="loading-conversations">
              <Loader2 className="spin" size={24} />
              <p>Loading...</p>
            </div>
          ) : conversations.length === 0 ? (
            <div className="no-conversations">
              <MessageCircle size={48} />
              <p>No conversations yet</p>
              <p className="hint">Start a new chat with GANESHA</p>
            </div>
          ) : (
            conversations.map(conv => (
              <div
                key={conv.id}
                className={`conversation-item ${currentConversation?.id === conv.id ? 'active' : ''}`}
                onClick={() => setCurrentConversation(conv)}
              >
                <div className="conversation-preview">
                  <p className="preview-text">{conv.preview || 'New conversation'}</p>
                  <div className="conversation-meta">
                    <span className="message-count">{conv.message_count || 0} messages</span>
                    <span className="conversation-time">{formatTimestamp(conv.updated_at)}</span>
                  </div>
                </div>
                <button
                  className="btn-delete-conv"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteConversation(conv.id);
                  }}
                  title="Delete conversation"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        <div className="chat-header">
          <div className="chat-title">
            <Sparkles size={20} className="ganesha-icon" />
            <div>
              <h1>GANESHA Command Center</h1>
              {currentDepartment && (
                <p className="department-indicator">
                  <CheckCircle size={14} />
                  Routed to: {currentDepartment}
                </p>
              )}
            </div>
          </div>
          {currentConversation && messages.length > 0 && (
            <button 
              className="btn-clear" 
              onClick={handleClearConversation}
              title="Clear conversation"
            >
              <RefreshCw size={18} />
              Clear
            </button>
          )}
        </div>

        <div className="messages-container">
          {messages.length === 0 && !streamingMessage ? (
            <div className="empty-chat">
              <Sparkles size={64} className="ganesha-icon-large" />
              <h2>Welcome to GANESHA</h2>
              <p>Your AI orchestrator for Kailash</p>
              <div className="sample-prompts">
                <p className="prompts-title">Try asking:</p>
                <button 
                  className="sample-prompt"
                  onClick={() => setInputMessage('What is the current status of the KAILASH project?')}
                >
                  "What is the current status of the KAILASH project?"
                </button>
                <button 
                  className="sample-prompt"
                  onClick={() => setInputMessage('Show me department workload distribution')}
                >
                  "Show me department workload distribution"
                </button>
                <button 
                  className="sample-prompt"
                  onClick={() => setInputMessage('Create a new task for SURYA department')}
                >
                  "Create a new task for SURYA department"
                </button>
              </div>
            </div>
          ) : (
            <div className="messages-list">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-content">
                    <p>{msg.content}</p>
                    {msg.department && (
                      <span className="message-department">
                        <CheckCircle size={12} />
                        {msg.department}
                      </span>
                    )}
                  </div>
                  <span className="message-time">{formatTimestamp(msg.timestamp)}</span>
                </div>
              ))}
              
              {streamingMessage && (
                <div className="message assistant streaming">
                  <div className="message-content">
                    <p>{streamingMessage}</p>
                    <span className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}

          {error && (
            <div className="error-message">
              <AlertCircle size={18} />
              {error}
            </div>
          )}
        </div>

        <form className="chat-input-form" onSubmit={handleSendMessage}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask GANESHA anything..."
            disabled={isLoading}
            className="chat-input"
          />
          <button 
            type="submit" 
            className="btn-send"
            disabled={isLoading || !inputMessage.trim()}
          >
            {isLoading ? (
              <Loader2 className="spin" size={20} />
            ) : (
              <Send size={20} />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
