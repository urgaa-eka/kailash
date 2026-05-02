import React, { useState, useEffect } from 'react';
import { 
  X, Users, AlertTriangle, CheckCircle, Clock, 
  Activity, Wifi, BarChart3, Target, TrendingUp
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Progress Bar Component for Tasks
const ProgressBar = ({ progress, status }) => {
  const getProgressColor = () => {
    if (status === 'completed') return 'bg-green-500';
    if (status === 'in_progress') return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  return (
    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
      <div 
        className={`h-full ${getProgressColor()} transition-all duration-300`}
        style={{ width: `${progress}%` }}
      />
    </div>
  );
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const colors = {
    active: 'bg-green-100 text-green-700',
    idle: 'bg-yellow-100 text-yellow-700',
    offline: 'bg-gray-100 text-gray-500',
    completed: 'bg-green-100 text-green-700',
    in_progress: 'bg-yellow-100 text-yellow-700',
    pending: 'bg-gray-100 text-gray-500',
    high: 'bg-red-100 text-red-700',
    medium: 'bg-yellow-100 text-yellow-700',
    low: 'bg-blue-100 text-blue-700'
  };

  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${colors[status] || 'bg-gray-100 text-gray-500'}`}>
      {status?.replace('_', ' ')}
    </span>
  );
};

// Severity Badge for Gaps
const SeverityBadge = ({ severity }) => {
  const colors = {
    critical: 'bg-red-500 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-500 text-gray-900',
    low: 'bg-blue-500 text-white'
  };

  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${colors[severity] || 'bg-gray-100 text-gray-500'}`}>
      {severity}
    </span>
  );
};

const DepartmentDetailsPanel = ({ department, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    if (department) {
      fetchDepartmentDetails();
    }
  }, [department]);

  const fetchDepartmentDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('token');
      
      if (!token) {
        setError('Authentication required');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_URL}/api/departments/${department.id.toLowerCase()}/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        setData(result);
      } else {
        setError(`Failed to load: ${response.status}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Calculate progress percentage based on status
  const getTaskProgress = (status) => {
    if (status === 'completed') return 100;
    if (status === 'in_progress') return 65;
    return 20; // pending
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-xl p-6 animate-pulse">
        <div className="flex justify-between items-center mb-4">
          <div className="h-6 bg-gray-200 rounded w-32"></div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg">
            <X size={20} className="text-gray-500" />
          </button>
        </div>
        <div className="space-y-4">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-red-200 shadow-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-gray-900">{department?.name}</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg">
            <X size={20} className="text-gray-500" />
          </button>
        </div>
        <p className="text-red-600 text-sm">{error}</p>
        <button 
          onClick={fetchDepartmentDetails}
          className="mt-3 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-xl overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-100" style={{ background: '#0A3D62' }}>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-bold text-lg text-white">{data.department}</h3>
            <p className="text-xs text-white/70 mt-0.5">{data.scope.toUpperCase()} DEPARTMENT</p>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-white/10 rounded-lg transition-colors">
            <X size={18} className="text-white" />
          </button>
        </div>
        
        {/* KPI Cards Row */}
        <div className="grid grid-cols-4 gap-2 mt-4">
          <div className="bg-white/10 rounded-lg p-2 text-center">
            <div className="text-white text-lg font-bold">{Math.round((data.automation_rate || 0) * 100)}%</div>
            <div className="text-white/70 text-[9px]">Automation</div>
          </div>
          <div className="bg-white/10 rounded-lg p-2 text-center">
            <div className="text-orange-400 text-lg font-bold">{data.gaps?.length || 0}</div>
            <div className="text-white/70 text-[9px]">Active Gaps</div>
          </div>
          <div className="bg-white/10 rounded-lg p-2 text-center">
            <div className="text-white text-lg font-bold">{data.tasks?.length || 0}</div>
            <div className="text-white/70 text-[9px]">Tasks</div>
          </div>
          <div className="bg-white/10 rounded-lg p-2 text-center">
            <div className="text-green-400 text-lg font-bold">{data.sub_agents?.length || 0}</div>
            <div className="text-white/70 text-[9px]">Team</div>
          </div>
        </div>
      </div>

      {/* Content - Two Column Grid */}
      <div className="p-4 grid grid-cols-2 gap-4 max-h-[400px] overflow-y-auto">
        {/* Left Column */}
        <div className="space-y-4">
          {/* Team Members (Sub-Agents) */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-3">
              <Users size={14} style={{ color: '#0A3D62' }} />
              <h4 className="font-semibold text-sm" style={{ color: '#0A3D62' }}>Team Members</h4>
              <span className="ml-auto text-xs text-gray-500">{data.sub_agents?.length || 0} agents</span>
            </div>
            
            {data.sub_agents?.length > 0 ? (
              <div className="space-y-2">
                {data.sub_agents.map((agent, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-2 border border-gray-100">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-white text-xs"
                           style={{ background: '#F47216' }}>
                        {agent.name?.charAt(0) || 'A'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-xs text-gray-900 truncate">{agent.name}</span>
                          <StatusBadge status={agent.status} />
                        </div>
                        <p className="text-[10px] text-gray-500 truncate">{agent.role}</p>
                      </div>
                    </div>
                    {agent.current_task && (
                      <p className="text-[10px] text-gray-600 mt-1.5 pl-10 truncate">
                        <span className="text-gray-400">Working on:</span> {agent.current_task}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 text-center py-2">No team members assigned</p>
            )}
          </div>

          {/* Ongoing Tasks with Progress */}
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-3">
              <Target size={14} style={{ color: '#F47216' }} />
              <h4 className="font-semibold text-sm" style={{ color: '#0A3D62' }}>Ongoing Tasks</h4>
            </div>
            
            {data.tasks?.length > 0 ? (
              <div className="space-y-2">
                {data.tasks.slice(0, 4).map((task, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-2 border border-gray-100">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-xs text-gray-900 truncate flex-1">{task.title}</span>
                      <StatusBadge status={task.priority} />
                    </div>
                    <p className="text-[10px] text-gray-500 mb-2 truncate">{task.description}</p>
                    <div className="flex items-center gap-2">
                      <ProgressBar progress={getTaskProgress(task.status)} status={task.status} />
                      <span className="text-[10px] font-medium text-gray-600 whitespace-nowrap">
                        {getTaskProgress(task.status)}%
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className="text-[9px] text-gray-400">
                        Assigned: {task.assigned_to}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 text-center py-2">No active tasks</p>
            )}
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-4">
          {/* Critical Issues (Gaps) */}
          <div className="bg-red-50 rounded-lg p-3 border border-red-100">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={14} className="text-red-600" />
              <h4 className="font-semibold text-sm text-red-700">Critical Issues</h4>
              <span className="ml-auto text-xs text-red-500">{data.gaps?.length || 0} gaps</span>
            </div>
            
            {data.gaps?.length > 0 ? (
              <div className="space-y-2">
                {data.gaps.slice(0, 3).map((gap, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-2 border border-red-100">
                    <div className="flex items-center gap-2 mb-1">
                      <SeverityBadge severity={gap.severity} />
                      <span className="font-medium text-xs text-gray-900 truncate flex-1">{gap.title}</span>
                    </div>
                    <p className="text-[10px] text-gray-600 truncate">{gap.description}</p>
                    <div className="flex items-center gap-3 mt-1.5 text-[9px]">
                      <span className="text-gray-400">Category: {gap.category}</span>
                      {gap.alerted_to_ganesha && (
                        <span className="text-yellow-600">✓ GANESHA notified</span>
                      )}
                      {gap.alerted_to_parvati && (
                        <span className="text-orange-600">✓ PARVATI escalated</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-green-600 text-center py-2 flex items-center justify-center gap-1">
                <CheckCircle size={12} /> No critical issues
              </p>
            )}
          </div>

          {/* Connected API Sources */}
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
            <div className="flex items-center gap-2 mb-3">
              <Wifi size={14} className="text-blue-600" />
              <h4 className="font-semibold text-sm text-blue-700">Connected APIs</h4>
            </div>
            
            {data.api_sources?.length > 0 ? (
              <div className="space-y-2">
                {data.api_sources.slice(0, 3).map((source, idx) => (
                  <div key={idx} className="bg-white rounded-lg p-2 border border-blue-100">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-xs text-gray-900">{source.name}</span>
                      <span className="text-[9px] px-1.5 py-0.5 bg-green-100 text-green-700 rounded">
                        {source.update_frequency}
                      </span>
                    </div>
                    <p className="text-[10px] text-gray-500 truncate">{source.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 text-center py-2">No API sources configured</p>
            )}
          </div>

          {/* Daily Activities */}
          <div className="bg-green-50 rounded-lg p-3 border border-green-100">
            <div className="flex items-center gap-2 mb-3">
              <Activity size={14} className="text-green-600" />
              <h4 className="font-semibold text-sm text-green-700">Daily Activities</h4>
            </div>
            
            {data.daily_tasks?.length > 0 ? (
              <ul className="space-y-1.5">
                {data.daily_tasks.map((task, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-[11px] text-gray-700">
                    <CheckCircle size={12} className="text-green-500 mt-0.5 flex-shrink-0" />
                    <span>{task}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-gray-500 text-center py-2">No daily activities</p>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <span className="text-[10px] text-gray-400">
          Last updated: {data.last_updated ? new Date(data.last_updated).toLocaleString() : 'N/A'}
        </span>
        <button 
          onClick={onClose}
          className="px-3 py-1 text-xs text-gray-600 hover:bg-gray-200 rounded transition-colors"
        >
          Close Panel
        </button>
      </div>
    </div>
  );
};

export default DepartmentDetailsPanel;
