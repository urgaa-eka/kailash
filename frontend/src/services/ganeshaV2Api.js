/**
 * GANESHA v2 API Service
 * Handles all communication with the RAG-enhanced orchestrator
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Get authentication headers
 */
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
};

/**
 * Stream orchestration response with SSE
 * @param {string} message - User message
 * @param {Array} conversationHistory - Previous messages
 * @param {string} productContext - URGAA, GSTSAAS, IGNITION, ARJUN
 * @param {Function} onEvent - Callback for each SSE event
 */
export const streamOrchestration = async (
  message,
  conversationHistory = [],
  productContext = null,
  onEvent
) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${API_URL}/api/v2/ganesha/orchestrate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_message: message,
      conversation_history: conversationHistory,
      product_context: productContext
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          onEvent(data);
        } catch (e) {
          console.warn('Failed to parse SSE event:', line);
        }
      }
    }
  }
};

/**
 * Query a specific agent directly
 */
export const queryAgent = async (agentId, query, context = {}) => {
  const response = await fetch(`${API_URL}/api/v2/ganesha/agent/query`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      agent_id: agentId,
      query,
      context
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

/**
 * List all available agents
 */
export const listAgents = async (product = null) => {
  const url = product 
    ? `${API_URL}/api/v2/ganesha/agents?product=${product}`
    : `${API_URL}/api/v2/ganesha/agents`;
    
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

/**
 * Get specific agent details
 */
export const getAgentDetails = async (agentId) => {
  const response = await fetch(`${API_URL}/api/v2/ganesha/agents/${agentId}`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

/**
 * Preview routing for a query
 */
export const previewRouting = async (query, product = null) => {
  const params = new URLSearchParams({ query });
  if (product) params.append('product', product);

  const response = await fetch(`${API_URL}/api/v2/ganesha/route/preview?${params}`, {
    method: 'POST',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

/**
 * Get RAG statistics
 */
export const getRAGStats = async () => {
  const response = await fetch(`${API_URL}/api/v2/ganesha/rag/stats`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

/**
 * Get conversation history
 */
export const getConversationHistory = async (limit = 20, product = null) => {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (product) params.append('product', product);

  const response = await fetch(`${API_URL}/api/v2/ganesha/history?${params}`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

/**
 * Get usage statistics
 */
export const getUsageStats = async () => {
  const response = await fetch(`${API_URL}/api/v2/ganesha/stats`, {
    method: 'GET',
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

/**
 * Quick action handler
 */
export const quickAction = async (action) => {
  const response = await fetch(`${API_URL}/api/v2/ganesha/quick-action`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ action })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Agent Icons mapping
export const AGENT_ICONS = {
  // URGAA
  'U-AI-01': '☀️', // SURYA - Revenue
  'U-AI-02': '🌊', // VARUNA - Demand
  'U-AI-03': '💰', // KUBER - Pricing
  'U-AI-04': '🌍', // BHUMI - Site
  'U-AI-05': '💨', // VAYU - Tasks
  'U-AI-06': '🔥', // AGNI - Health
  'U-AI-07': '🔱', // SHIV - Auto-Rectify
  'U-AI-08': '🔧', // VISHWAKARMA - Troubleshoot
  
  // GSTSAAS
  'G-AI-01': '🪷', // LAKSHMI - Profit
  'G-AI-02': '💊', // DHANVANTARI - Cash Flow
  'G-AI-03': '📢', // NARADA - Churn
  'G-AI-04': '♟️', // CHANAKYA - Opportunity
  'G-AI-05': '📜', // BRIHASPATI - Quote
  'G-AI-06': '📝', // VYASA - Follow-up
  'G-AI-07': '📦', // KUBERA - Reorder
  'G-AI-08': '🏪', // VAISRAVANA - Vendor
  'G-AI-09': '🩺', // ASHWINI - Repair
  'G-AI-10': '🎓', // GURU - Skills
  
  // IGNITION
  'I-AI-01': '📚', // SARASWATI - Charger Rec
  'I-AI-02': '🐒', // HANUMAN - Routes
  'I-AI-03': '💵', // ARTHA - Expenses
  'I-AI-04': '🏔️', // PARVATI - Workshop
  'I-AI-05': '🐘', // GANESHA-C - Consumer Chat
  'I-AI-06': '⚔️', // KARNA - Shift
  'I-AI-07': '⚡', // INDRA - Fleet Report
  'I-AI-08': '⚖️', // YAMA - Fleet Health
  'I-AI-09': '🪙', // DHANA - Fleet Cost
  
  // ARJUN
  'A-AI-01': '📖', // VIDYA - Course
  'A-AI-02': '🏹', // DRONA - Adaptive
  'A-AI-03': '🎯', // ARJUNA - Practice
  'A-AI-04': '📋', // CHITRAGUPTA - Certification
  'A-AI-05': '🪓', // PARASHURAMA - Skill Gap
  'A-AI-06': '🐎', // NAKULA - Career
  'A-AI-07': '📊', // SAHADEVA - Batch
  'A-AI-08': '🛡️', // BHISHMA - Employer
  
  // Master
  'GANESHA': '🙏'
};

// Product Colors - Matching existing design system
export const PRODUCT_COLORS = {
  'URGAA': '#0A3D62',      // Blue (matching existing primary)
  'GSTSAAS': '#417E46',    // Green (from brand palette)
  'IGNITION': '#DF8C4D',   // Orange (from brand palette)
  'ARJUN': '#8172AD',      // Light purple (from brand palette)
  'ALL': '#64748b'         // Gray (matching existing secondary)
};

export default {
  streamOrchestration,
  queryAgent,
  listAgents,
  getAgentDetails,
  previewRouting,
  getRAGStats,
  getConversationHistory,
  getUsageStats,
  quickAction,
  AGENT_ICONS,
  PRODUCT_COLORS
};
