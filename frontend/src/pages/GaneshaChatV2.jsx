import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Send, Mic, MicOff, Paperclip, Brain, Zap, Globe,
  FileText, X, ChevronDown, Loader, ArrowLeft,
  CheckCircle, AlertCircle, Database, Cpu, Users,
  Sparkles, Bot, Target, Activity, Info
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { 
  streamOrchestration, 
  listAgents, 
  previewRouting,
  getRAGStats,
  quickAction,
  AGENT_ICONS,
  PRODUCT_COLORS 
} from '../services/ganeshaV2Api';
import './GaneshaChatV2.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Product options for context selection - Matching existing design system
const PRODUCT_OPTIONS = [
  { id: null, name: 'Auto-Detect', icon: <Brain size={16} />, color: '#64748b' },
  { id: 'URGAA', name: 'URGAA', icon: <Zap size={16} />, color: '#0A3D62', desc: 'EV Infrastructure' },
  { id: 'GSTSAAS', name: 'GSTSAAS', icon: <FileText size={16} />, color: '#417E46', desc: 'Workshop Management' },
  { id: 'IGNITION', name: 'IGNITION', icon: <Globe size={16} />, color: '#DF8C4D', desc: 'Consumer App' },
  { id: 'ARJUN', name: 'ARJUN', icon: <Users size={16} />, color: '#8172AD', desc: 'Training Platform' },
];

// Quick action buttons
const QUICK_ACTIONS = [
  { id: 'status', label: 'System Status', icon: <Activity size={14} /> },
  { id: 'revenue', label: 'Revenue', icon: <Zap size={14} /> },
  { id: 'alerts', label: 'Alerts', icon: <AlertCircle size={14} /> },
  { id: 'agents', label: 'View Agents', icon: <Users size={14} /> },
];

const GaneshaChatV2 = () => {
  // State
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showProductSelector, setShowProductSelector] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState(null);
  const [currentPhase, setCurrentPhase] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [ragStats, setRagStats] = useState(null);
  const [showAgentPanel, setShowAgentPanel] = useState(false);
  const [agents, setAgents] = useState([]);
  
  // Refs
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingIntervalRef = useRef(null);

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage, scrollToBottom]);

  // Load RAG stats on mount
  useEffect(() => {
    const loadRAGStats = async () => {
      try {
        const stats = await getRAGStats();
        setRagStats(stats);
      } catch (e) {
        console.error('Failed to load RAG stats:', e);
      }
    };
    loadRAGStats();
  }, []);

  // Load agents on mount
  useEffect(() => {
    const loadAgents = async () => {
      try {
        const data = await listAgents();
        setAgents(data.agents || []);
      } catch (e) {
        console.error('Failed to load agents:', e);
      }
    };
    loadAgents();
  }, []);

  // Voice Recording Functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported('audio/webm') 
        ? 'audio/webm' 
        : MediaRecorder.isTypeSupported('audio/mp4') 
          ? 'audio/mp4' 
          : 'audio/ogg';
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(1000);
      setIsRecording(true);
      setRecordingTime(0);
      
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please allow microphone access.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setIsTranscribing(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      const mimeType = audioBlob.type;
      const extension = mimeType.includes('webm') ? 'webm' : mimeType.includes('mp4') ? 'mp4' : 'ogg';
      formData.append('file', audioBlob, `voice_recording.${extension}`);

      const response = await fetch(`${API_URL}/api/ganesha/voice`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success' && data.transcription) {
          setInput(prev => prev ? `${prev} ${data.transcription}` : data.transcription);
        }
      }
    } catch (error) {
      console.error('Transcription error:', error);
    } finally {
      setIsTranscribing(false);
      setRecordingTime(0);
    }
  };

  const formatRecordingTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // File handling
  const handleFileAttach = (e) => {
    const files = Array.from(e.target.files);
    setAttachments(prev => [...prev, ...files]);
  };

  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  // Send message with streaming
  const handleSend = async () => {
    if (!input.trim() && attachments.length === 0) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input,
      attachments: attachments.map(f => f.name),
      timestamp: new Date(),
      product: selectedProduct
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setAttachments([]);
    setIsLoading(true);
    setStreamingMessage({ role: 'assistant', content: '', phases: [] });
    setCurrentPhase('thinking');

    try {
      const token = localStorage.getItem('token');
      
      // Handle file uploads (OCR) first
      let fullQuery = currentInput;
      for (const file of attachments) {
        try {
          const formData = new FormData();
          formData.append('file', file);
          const ocrRes = await fetch(`${API_URL}/api/ganesha/ocr`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
          });
          if (ocrRes.ok) {
            const ocrData = await ocrRes.json();
            fullQuery += `\n\n[Document: ${file.name}]\n${ocrData.extracted_text}`;
          }
        } catch (e) {
          console.error('OCR error:', e);
        }
      }

      // Build conversation history
      const history = messages.slice(-10).map(m => ({
        role: m.role,
        content: m.content
      }));

      // Stream the response
      let assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        agentId: null,
        agentName: null,
        specialty: null,
        ragUsed: false,
        ragSources: [],
        product: null,
        phases: [],
        timestamp: new Date()
      };

      await streamOrchestration(
        fullQuery,
        history,
        selectedProduct,
        (event) => {
          // Handle different event types
          switch (event.type) {
            case 'thinking':
              setCurrentPhase('thinking');
              assistantMessage.phases.push({ type: 'thinking', timestamp: event.timestamp });
              break;
              
            case 'rag_complete':
              setCurrentPhase('rag');
              assistantMessage.ragUsed = true;
              assistantMessage.ragSources = event.sources || [];
              assistantMessage.phases.push({ type: 'rag', sources: event.sources_count });
              break;
              
            case 'routing':
              setCurrentPhase('routing');
              assistantMessage.agentId = event.agent_id;
              assistantMessage.agentName = event.agent_name;
              assistantMessage.specialty = event.specialty;
              assistantMessage.product = event.product;
              assistantMessage.phases.push({ 
                type: 'routing', 
                agent: event.agent_name 
              });
              break;
              
            case 'agent_response':
              setCurrentPhase('responding');
              assistantMessage.content += event.content || '';
              setStreamingMessage({ ...assistantMessage });
              break;
              
            case 'complete':
              setCurrentPhase(null);
              assistantMessage.content = event.full_response || assistantMessage.content;
              break;
              
            case 'error':
              assistantMessage.content = `Error: ${event.message}`;
              assistantMessage.isError = true;
              break;
              
            default:
              // Handle raw content chunks
              if (event.content) {
                assistantMessage.content += event.content;
                setStreamingMessage({ ...assistantMessage });
              }
          }
        }
      );

      // Finalize message
      setMessages(prev => [...prev, assistantMessage]);
      setStreamingMessage(null);

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: `I encountered an error: ${error.message}. Please try again.`,
        isError: true,
        timestamp: new Date()
      }]);
      setStreamingMessage(null);
    } finally {
      setIsLoading(false);
      setCurrentPhase(null);
    }
  };

  // Quick action handler
  const handleQuickAction = async (actionId) => {
    if (actionId === 'agents') {
      setShowAgentPanel(true);
      return;
    }

    try {
      const result = await quickAction(actionId);
      if (result.message) {
        setInput(result.message);
      }
    } catch (e) {
      console.error('Quick action error:', e);
    }
  };

  // Key press handler
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Get agent icon
  const getAgentIcon = (agentId) => {
    return AGENT_ICONS[agentId] || '🤖';
  };

  // Get product color
  const getProductColor = (product) => {
    return PRODUCT_COLORS[product] || '#6B7280';
  };

  // Phase indicator component
  const PhaseIndicator = ({ phase }) => {
    const phases = {
      thinking: { label: 'Analyzing...', icon: <Brain size={14} /> },
      rag: { label: 'Searching knowledge...', icon: <Database size={14} /> },
      routing: { label: 'Routing to specialist...', icon: <Target size={14} /> },
      responding: { label: 'Generating response...', icon: <Sparkles size={14} /> }
    };

    const current = phases[phase];
    if (!current) return null;

    return (
      <div className="phase-indicator">
        <span className="phase-icon">{current.icon}</span>
        <span className="phase-label">{current.label}</span>
        <span className="phase-dots">
          <span className="dot"></span>
          <span className="dot"></span>
          <span className="dot"></span>
        </span>
      </div>
    );
  };

  return (
    <div className="ganesha-chat-v2">
      {/* Header */}
      <div className="chat-header">
        <div className="header-left">
          <Link to="/dashboard/executive" className="back-btn">
            <ArrowLeft size={18} />
          </Link>
          <div className="header-icon">
            <Brain size={28} />
          </div>
          <div className="header-info">
            <h1>GANESHA <span className="version-badge">v2.0</span></h1>
            <p>RAG-Enhanced AI Orchestrator — 36 Specialist Agents</p>
          </div>
        </div>

        {/* RAG Status Indicator */}
        {ragStats && (
          <div className="rag-status" title={`${ragStats.stats?.total_vectors || 0} knowledge vectors`}>
            <Database size={14} />
            <span>{ragStats.status === 'connected' ? 'Knowledge Base Active' : 'Offline'}</span>
            <span className={`status-dot ${ragStats.status}`}></span>
          </div>
        )}

        {/* Product Context Selector */}
        <div className="product-selector-wrapper">
          <button 
            className="product-selector-btn"
            onClick={() => setShowProductSelector(!showProductSelector)}
            style={{ borderColor: getProductColor(selectedProduct) }}
          >
            <span className="product-icon">
              {PRODUCT_OPTIONS.find(p => p.id === selectedProduct)?.icon}
            </span>
            <span>{PRODUCT_OPTIONS.find(p => p.id === selectedProduct)?.name || 'Auto-Detect'}</span>
            <ChevronDown size={14} />
          </button>
          
          {showProductSelector && (
            <div className="product-dropdown">
              {PRODUCT_OPTIONS.map(product => (
                <button
                  key={product.id || 'auto'}
                  className={`product-option ${selectedProduct === product.id ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedProduct(product.id);
                    setShowProductSelector(false);
                  }}
                  style={{ '--product-color': product.color }}
                >
                  <span className="product-icon">{product.icon}</span>
                  <div className="product-info">
                    <span className="product-name">{product.name}</span>
                    {product.desc && <span className="product-desc">{product.desc}</span>}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Agent Panel Toggle */}
        <button 
          className="agent-panel-toggle"
          onClick={() => setShowAgentPanel(!showAgentPanel)}
          title="View AI Agents"
        >
          <Users size={18} />
          <span>36</span>
        </button>
      </div>

      {/* Messages Area */}
      <div className="chat-messages">
        {messages.length === 0 && !streamingMessage && (
          <div className="empty-state">
            <div className="empty-icon">
              <Brain size={56} />
              <Sparkles className="sparkle" size={20} />
            </div>
            <h2>Welcome to GANESHA v2.0</h2>
            <p>Enhanced with RAG knowledge retrieval and 36 specialist AI agents</p>
            
            {/* Quick Actions */}
            <div className="quick-actions">
              {QUICK_ACTIONS.map(action => (
                <button
                  key={action.id}
                  className="quick-action-btn"
                  onClick={() => handleQuickAction(action.id)}
                >
                  {action.icon}
                  <span>{action.label}</span>
                </button>
              ))}
            </div>

            {/* Product Cards */}
            <div className="product-cards">
              {PRODUCT_OPTIONS.filter(p => p.id).map(product => (
                <button
                  key={product.id}
                  className="product-card"
                  onClick={() => setSelectedProduct(product.id)}
                  style={{ '--product-color': product.color }}
                >
                  <span className="card-icon">{product.icon}</span>
                  <span className="card-name">{product.name}</span>
                  <span className="card-desc">{product.desc}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className={`message-bubble ${msg.isError ? 'error' : ''}`}>
              {/* Agent Header for assistant messages */}
              {msg.role === 'assistant' && msg.agentId && (
                <div 
                  className="agent-header"
                  style={{ '--agent-color': getProductColor(msg.product) }}
                >
                  <span className="agent-icon">{getAgentIcon(msg.agentId)}</span>
                  <span className="agent-name">{msg.agentName}</span>
                  <span className="agent-id">({msg.agentId})</span>
                  {msg.specialty && (
                    <span className="agent-specialty">{msg.specialty}</span>
                  )}
                </div>
              )}
              
              {/* Message Content */}
              <div className="message-content">
                {msg.content.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
              
              {/* Attachments for user messages */}
              {msg.role === 'user' && msg.attachments?.length > 0 && (
                <div className="message-attachments">
                  {msg.attachments.map((name, i) => (
                    <span key={i} className="attachment-tag">
                      <FileText size={12} /> {name}
                    </span>
                  ))}
                </div>
              )}
              
              {/* Metadata for assistant messages */}
              {msg.role === 'assistant' && !msg.isError && (
                <div className="message-meta">
                  {/* RAG Indicator */}
                  {msg.ragUsed && (
                    <div className="meta-tag rag">
                      <Database size={12} />
                      <span>Knowledge-enhanced</span>
                      {msg.ragSources?.length > 0 && (
                        <span className="source-count">{msg.ragSources.length} sources</span>
                      )}
                    </div>
                  )}
                  
                  {/* Product Tag */}
                  {msg.product && (
                    <span 
                      className="meta-tag product"
                      style={{ backgroundColor: getProductColor(msg.product) }}
                    >
                      {msg.product}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Streaming Message */}
        {streamingMessage && (
          <div className="message assistant streaming">
            <div className="message-bubble">
              {streamingMessage.agentId && (
                <div 
                  className="agent-header"
                  style={{ '--agent-color': getProductColor(streamingMessage.product) }}
                >
                  <span className="agent-icon">{getAgentIcon(streamingMessage.agentId)}</span>
                  <span className="agent-name">{streamingMessage.agentName}</span>
                </div>
              )}
              
              {currentPhase && <PhaseIndicator phase={currentPhase} />}
              
              {streamingMessage.content && (
                <div className="message-content streaming">
                  {streamingMessage.content.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                  <span className="cursor">▊</span>
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Agent Panel Sidebar */}
      {showAgentPanel && (
        <div className="agent-panel">
          <div className="panel-header">
            <h3><Users size={18} /> AI Agents</h3>
            <button onClick={() => setShowAgentPanel(false)}><X size={18} /></button>
          </div>
          <div className="panel-content">
            {Object.entries(
              agents.reduce((acc, agent) => {
                const product = agent.product || 'OTHER';
                if (!acc[product]) acc[product] = [];
                acc[product].push(agent);
                return acc;
              }, {})
            ).map(([product, productAgents]) => (
              <div key={product} className="agent-group">
                <h4 style={{ color: getProductColor(product) }}>{product}</h4>
                {productAgents.map(agent => (
                  <div 
                    key={agent.agent_id} 
                    className="agent-item"
                    onClick={() => {
                      setInput(`@${agent.name}: `);
                      setShowAgentPanel(false);
                    }}
                  >
                    <span className="agent-icon">{getAgentIcon(agent.agent_id)}</span>
                    <div className="agent-info">
                      <span className="agent-name">{agent.name}</span>
                      <span className="agent-specialty">{agent.specialty}</span>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Attachments Preview */}
      {attachments.length > 0 && (
        <div className="attachments-preview">
          {attachments.map((file, idx) => (
            <div key={idx} className="attachment-item">
              <FileText size={16} />
              <span>{file.name}</span>
              <button onClick={() => removeAttachment(idx)}>
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="chat-input-area">
        <div className="input-container">
          {/* Attach Button */}
          <button 
            className="input-action-btn"
            onClick={() => fileInputRef.current?.click()}
            title="Attach PDF or Image (OCR)"
          >
            <Paperclip size={20} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={handleFileAttach}
            className="hidden-input"
          />

          {/* Voice Button */}
          <button 
            className={`input-action-btn ${isRecording ? 'recording' : ''} ${isTranscribing ? 'transcribing' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isTranscribing}
            title={isRecording ? `Recording ${formatRecordingTime(recordingTime)}` : 'Voice input'}
          >
            {isTranscribing ? <Loader size={20} className="spin" /> : isRecording ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          
          {isRecording && (
            <div className="recording-indicator">
              <span className="recording-dot"></span>
              <span>{formatRecordingTime(recordingTime)}</span>
            </div>
          )}

          {/* Text Input */}
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask GANESHA anything... (36 specialist agents ready)"
            className="chat-input"
            rows={1}
          />

          {/* Send Button */}
          <button 
            className={`send-btn ${(input.trim() || attachments.length > 0) ? 'active' : ''}`}
            onClick={handleSend}
            disabled={isLoading || (!input.trim() && attachments.length === 0)}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default GaneshaChatV2;
