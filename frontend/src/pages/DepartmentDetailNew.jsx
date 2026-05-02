import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { DEPARTMENT_ICONS, UI_ICONS } from '../data/departmentIcons';
import { useAuthStore } from '../stores/authStore';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const DepartmentDetailNew = () => {
  const { name } = useParams();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [departmentData, setDepartmentData] = useState(null);
  const [error, setError] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    fetchDepartmentSummary();
  }, [name]);

  const fetchDepartmentSummary = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/departments/${name.toLowerCase()}/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const responseText = await response.text();
      if (response.ok) {
        const data = JSON.parse(responseText);
        setDepartmentData(data);
      } else {
        setError('Failed to load department data');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-500',
      high: 'bg-orange-500',
      medium: 'bg-yellow-500',
      low: 'bg-blue-500'
    };
    return colors[severity] || 'bg-gray-500';
  };

  const getStatusColor = (status) => {
    const colors = {
      completed: 'text-green-400',
      in_progress: 'text-yellow-400',
      pending: 'text-gray-400'
    };
    return colors[status] || 'text-gray-400';
  };

  const renderIcon = (svgString) => (
    <span dangerouslySetInnerHTML={{ __html: svgString }} />
  );

  const departmentIcon = DEPARTMENT_ICONS[name?.toUpperCase()] || DEPARTMENT_ICONS.GANESHA;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading department data...</div>
      </div>
    );
  }

  if (error || !departmentData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">{error || 'Department not found'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-md border-b border-purple-500/30 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/dashboard/executive" className="text-purple-400 hover:text-purple-300 transition-colors">
                {renderIcon(UI_ICONS.ARROW_LEFT)}
              </Link>
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 text-purple-400">
                  {renderIcon(departmentIcon)}
                </span>
                <div>
                  <h1 className="text-2xl font-bold text-white">{departmentData.department}</h1>
                  <p className="text-sm text-purple-300">{departmentData.scope.toUpperCase()} DEPARTMENT</p>
                </div>
              </div>
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-3 px-4 py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center text-white font-bold">
                  {user?.full_name?.charAt(0) || 'U'}
                </div>
                <span className="text-white font-medium">{user?.full_name}</span>
                <span className="text-purple-300">▼</span>
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-xl border border-purple-500/30 py-2">
                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-2 text-left text-white hover:bg-purple-500/20 transition-colors flex items-center gap-2"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Department Overview */}
        <div className="bg-black/30 backdrop-blur-md rounded-xl border border-purple-500/30 p-6">
          <h2 className="text-xl font-bold text-white mb-4">Department Overview</h2>
          <p className="text-purple-200 mb-4">{departmentData.description}</p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-purple-500/10 rounded-lg p-4">
              <div className="text-purple-300 text-sm mb-1">Automation Rate</div>
              <div className="text-2xl font-bold text-white">{(departmentData.automation_rate * 100).toFixed(0)}%</div>
            </div>
            <div className="bg-purple-500/10 rounded-lg p-4">
              <div className="text-purple-300 text-sm mb-1">Active Gaps</div>
              <div className="text-2xl font-bold text-white">{departmentData.gaps.length}</div>
            </div>
            <div className="bg-purple-500/10 rounded-lg p-4">
              <div className="text-purple-300 text-sm mb-1">Active Tasks</div>
              <div className="text-2xl font-bold text-white">{departmentData.tasks.length}</div>
            </div>
            <div className="bg-purple-500/10 rounded-lg p-4">
              <div className="text-purple-300 text-sm mb-1">Sub-Agents</div>
              <div className="text-2xl font-bold text-white">{departmentData.sub_agents.length}</div>
            </div>
          </div>
        </div>

        {/* Latest Intelligence */}
        {departmentData.latest_intelligence && (
          <div className="bg-black/30 backdrop-blur-md rounded-xl border border-purple-500/30 p-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-yellow-400 text-xl">💡</span>
              <h2 className="text-xl font-bold text-white">Latest Intelligence</h2>
              <span className="text-xs text-purple-300 ml-auto">Updated Daily</span>
            </div>
            <div className="text-purple-200 text-sm leading-relaxed">
              {departmentData.latest_intelligence}
            </div>
          </div>
        )}

        {/* API Sources */}
        {departmentData.api_sources.length > 0 && (
          <div className="bg-black/30 backdrop-blur-md rounded-xl border border-purple-500/30 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Connected API Sources</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {departmentData.api_sources.map((source, idx) => (
                <div key={idx} className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/20">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-white font-semibold">{source.name}</h3>
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                      {source.update_frequency}
                    </span>
                  </div>
                  <p className="text-purple-300 text-sm mb-2">{source.description}</p>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-purple-400">Type: {source.type}</span>
                    {source.auth_required && (
                      <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded">Auth Required</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Gaps & Issues */}
        {departmentData.gaps.length > 0 && (
          <div className="bg-black/30 backdrop-blur-md rounded-xl border border-red-500/30 p-6">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-red-400 text-xl">⚠️</span>
              <h2 className="text-xl font-bold text-white">Detected Gaps & Issues</h2>
            </div>
            <div className="space-y-3">
              {departmentData.gaps.map((gap, idx) => (
                <div key={idx} className="bg-red-500/10 rounded-lg p-4 border border-red-500/30">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${getSeverityColor(gap.severity)}`}></span>
                      <h3 className="text-white font-semibold">{gap.title}</h3>
                    </div>
                    <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded uppercase">
                      {gap.severity}
                    </span>
                  </div>
                  <p className="text-purple-200 text-sm mb-2">{gap.description}</p>
                  <div className="flex items-center gap-4 text-xs text-purple-400">
                    <span>Category: {gap.category}</span>
                    <span>Detected: {new Date(gap.detected_at).toLocaleDateString()}</span>
                    {gap.alerted_to_ganesha && <span className="text-yellow-400">✓ Alerted to GANESHA</span>}
                    {gap.alerted_to_parvati && <span className="text-orange-400">✓ Escalated to PARVATI</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Current Tasks */}
        {departmentData.tasks.length > 0 && (
          <div className="bg-black/30 backdrop-blur-md rounded-xl border border-purple-500/30 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Current Tasks</h2>
            <div className="space-y-3">
              {departmentData.tasks.map((task, idx) => (
                <div key={idx} className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/20">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-white font-semibold">{task.title}</h3>
                    <span className={`px-2 py-1 bg-purple-500/20 text-xs rounded uppercase ${getStatusColor(task.status)}`}>
                      {task.status.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-purple-200 text-sm mb-2">{task.description}</p>
                  <div className="flex items-center gap-4 text-xs text-purple-400">
                    <span>Assigned to: {task.assigned_to}</span>
                    <span>Priority: {task.priority}</span>
                    {task.due_date && <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sub-Agents */}
        {departmentData.sub_agents.length > 0 && (
          <div className="bg-black/30 backdrop-blur-md rounded-xl border border-purple-500/30 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Sub-Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {departmentData.sub_agents.map((agent, idx) => (
                <div key={idx} className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/20">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center text-white font-bold">
                      {agent.name.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-semibold">{agent.name}</h3>
                      <p className="text-purple-300 text-xs">{agent.role}</p>
                    </div>
                    <span className={`w-2 h-2 rounded-full ${
                      agent.status === 'active' ? 'bg-green-400' : 
                      agent.status === 'idle' ? 'bg-yellow-400' : 'bg-gray-400'
                    }`}></span>
                  </div>
                  {agent.current_task && (
                    <p className="text-purple-200 text-xs mt-2">Current: {agent.current_task}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Daily Tasks */}
        {departmentData.daily_tasks.length > 0 && (
          <div className="bg-black/30 backdrop-blur-md rounded-xl border border-purple-500/30 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Daily Tasks</h2>
            <ul className="space-y-2">
              {departmentData.daily_tasks.map((task, idx) => (
                <li key={idx} className="flex items-start gap-3 text-purple-200">
                  <span className="text-purple-400 mt-1">•</span>
                  <span>{task}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>
    </div>
  );
};

export default DepartmentDetailNew;
