import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  AlertTriangle, CheckCircle, Plus, Edit2, Trash2, X, 
  Target, Users, ArrowLeft, RefreshCw, Filter
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Modal Component
const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center" style={{ background: '#0A3D62' }}>
          <h2 className="text-lg font-bold text-white">{title}</h2>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg">
            <X size={20} className="text-white" />
          </button>
        </div>
        <div className="p-4 overflow-y-auto max-h-[calc(90vh-120px)]">
          {children}
        </div>
      </div>
    </div>
  );
};

const GapsTasksManagement = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  
  const [activeTab, setActiveTab] = useState('gaps');
  const [gaps, setGaps] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Modal states
  const [showGapModal, setShowGapModal] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  
  // Filter states
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Form states
  const [gapForm, setGapForm] = useState({
    department: '', title: '', description: '', severity: 'medium', category: 'api'
  });
  const [taskForm, setTaskForm] = useState({
    department: '', title: '', description: '', assigned_to: '', priority: 'medium', due_date: ''
  });

  const departments = [
    'lakshmi', 'vishwakarma', 'agni', 'indra', 'vayu', 'yama', 'kubera',
    'surya', 'brahma', 'saraswati', 'varuna', 'pragya', 'tvashta', 'kartikeya'
  ];

  useEffect(() => {
    fetchData();
  }, [departmentFilter, severityFilter, statusFilter]);

  const getToken = () => localStorage.getItem('token');

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = getToken();
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Build query params
      let gapParams = new URLSearchParams();
      let taskParams = new URLSearchParams();
      
      if (departmentFilter) {
        gapParams.append('department', departmentFilter);
        taskParams.append('department', departmentFilter);
      }
      if (severityFilter) gapParams.append('severity', severityFilter);
      if (statusFilter) taskParams.append('status', statusFilter);
      
      const [gapsRes, tasksRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/api/management/gaps?${gapParams}`, { headers }),
        fetch(`${API_URL}/api/management/tasks?${taskParams}`, { headers }),
        fetch(`${API_URL}/api/management/stats`, { headers })
      ]);
      
      if (gapsRes.ok) setGaps(await gapsRes.json());
      if (tasksRes.ok) setTasks(await tasksRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // GAP CRUD
  const handleCreateGap = async (e) => {
    e.preventDefault();
    try {
      const token = getToken();
      const response = await fetch(`${API_URL}/api/management/gaps`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(gapForm)
      });
      
      if (response.ok) {
        setShowGapModal(false);
        setGapForm({ department: '', title: '', description: '', severity: 'medium', category: 'api' });
        fetchData();
      }
    } catch (err) {
      alert('Error creating gap: ' + err.message);
    }
  };

  const handleUpdateGap = async (gapId, updates) => {
    try {
      const token = getToken();
      await fetch(`${API_URL}/api/management/gaps/${gapId}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      fetchData();
    } catch (err) {
      alert('Error updating gap: ' + err.message);
    }
  };

  const handleDeleteGap = async (gapId) => {
    if (!confirm('Are you sure you want to delete this gap?')) return;
    try {
      const token = getToken();
      await fetch(`${API_URL}/api/management/gaps/${gapId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchData();
    } catch (err) {
      alert('Error deleting gap: ' + err.message);
    }
  };

  // TASK CRUD
  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      const token = getToken();
      const response = await fetch(`${API_URL}/api/management/tasks`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(taskForm)
      });
      
      if (response.ok) {
        setShowTaskModal(false);
        setTaskForm({ department: '', title: '', description: '', assigned_to: '', priority: 'medium', due_date: '' });
        fetchData();
      }
    } catch (err) {
      alert('Error creating task: ' + err.message);
    }
  };

  const handleUpdateTask = async (taskId, updates) => {
    try {
      const token = getToken();
      await fetch(`${API_URL}/api/management/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      fetchData();
    } catch (err) {
      alert('Error updating task: ' + err.message);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      const token = getToken();
      await fetch(`${API_URL}/api/management/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchData();
    } catch (err) {
      alert('Error deleting task: ' + err.message);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-500 text-white',
      high: 'bg-orange-500 text-white',
      medium: 'bg-yellow-500 text-gray-900',
      low: 'bg-blue-500 text-white'
    };
    return colors[severity] || 'bg-gray-500 text-white';
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-gray-200 text-gray-700',
      in_progress: 'bg-yellow-200 text-yellow-800',
      completed: 'bg-green-200 text-green-800'
    };
    return colors[status] || 'bg-gray-200 text-gray-700';
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-40" style={{ borderTopColor: '#F47216', borderTopWidth: '3px' }}>
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/kailash')} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeft size={20} className="text-gray-600" />
            </button>
            <div>
              <h1 className="text-xl font-bold" style={{ color: '#0A3D62' }}>Gap & Task Management</h1>
              <p className="text-sm text-gray-500">Manage department gaps and tasks</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button onClick={fetchData} className="p-2 hover:bg-gray-100 rounded-lg" title="Refresh">
              <RefreshCw size={20} className="text-gray-600" />
            </button>
            <span className="text-sm text-gray-600">{user?.full_name}</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle size={18} className="text-red-500" />
                <span className="text-sm text-gray-500">Open Gaps</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{stats.gaps.open}</div>
              <div className="text-xs text-red-500">{stats.gaps.critical} critical</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle size={18} className="text-green-500" />
                <span className="text-sm text-gray-500">Resolved Gaps</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{stats.gaps.resolved}</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Target size={18} style={{ color: '#F47216' }} />
                <span className="text-sm text-gray-500">Pending Tasks</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{stats.tasks.pending}</div>
              <div className="text-xs text-yellow-600">{stats.tasks.in_progress} in progress</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle size={18} className="text-green-500" />
                <span className="text-sm text-gray-500">Completed Tasks</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{stats.tasks.completed}</div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setActiveTab('gaps')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'gaps' ? 'text-white' : 'bg-white text-gray-600 border border-gray-200'
            }`}
            style={activeTab === 'gaps' ? { background: '#0A3D62' } : {}}
          >
            <AlertTriangle size={16} className="inline mr-2" />
            Gaps ({gaps.length})
          </button>
          <button
            onClick={() => setActiveTab('tasks')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'tasks' ? 'text-white' : 'bg-white text-gray-600 border border-gray-200'
            }`}
            style={activeTab === 'tasks' ? { background: '#0A3D62' } : {}}
          >
            <Target size={16} className="inline mr-2" />
            Tasks ({tasks.length})
          </button>
        </div>

        {/* Filters & Actions */}
        <div className="bg-white rounded-lg p-4 border border-gray-200 mb-4 flex flex-wrap gap-3 items-center">
          <Filter size={18} className="text-gray-400" />
          <select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
          >
            <option value="">All Departments</option>
            {departments.map(d => (
              <option key={d} value={d}>{d.toUpperCase()}</option>
            ))}
          </select>
          
          {activeTab === 'gaps' && (
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          )}
          
          {activeTab === 'tasks' && (
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          )}
          
          <div className="flex-1"></div>
          
          <button
            onClick={() => activeTab === 'gaps' ? setShowGapModal(true) : setShowTaskModal(true)}
            className="px-4 py-2 text-white rounded-lg font-medium flex items-center gap-2 hover:opacity-90"
            style={{ background: '#F47216' }}
          >
            <Plus size={18} />
            Create {activeTab === 'gaps' ? 'Gap' : 'Task'}
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading...</div>
        ) : activeTab === 'gaps' ? (
          <div className="space-y-3">
            {gaps.length === 0 ? (
              <div className="text-center py-12 text-gray-500 bg-white rounded-lg border">No gaps found</div>
            ) : (
              gaps.map(gap => (
                <div key={gap.gap_id} className="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${getSeverityColor(gap.severity)}`}>
                          {gap.severity}
                        </span>
                        <span className="px-2 py-0.5 rounded text-xs font-semibold uppercase bg-gray-200 text-gray-700">
                          {gap.category}
                        </span>
                        <span className="text-xs text-gray-400">{gap.department.toUpperCase()}</span>
                      </div>
                      <h3 className="font-semibold text-gray-900">{gap.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">{gap.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                        <span>Detected: {new Date(gap.detected_at).toLocaleDateString()}</span>
                        {gap.alerted_to_ganesha && <span className="text-yellow-600">✓ GANESHA</span>}
                        {gap.alerted_to_parvati && <span className="text-orange-600">✓ PARVATI</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {!gap.resolved && (
                        <button
                          onClick={() => handleUpdateGap(gap.gap_id, { resolved: true })}
                          className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
                        >
                          Resolve
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteGap(gap.gap_id)}
                        className="p-2 hover:bg-red-50 rounded-lg text-red-500"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.length === 0 ? (
              <div className="text-center py-12 text-gray-500 bg-white rounded-lg border">No tasks found</div>
            ) : (
              tasks.map(task => (
                <div key={task.task_id} className="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${getStatusColor(task.status)}`}>
                          {task.status.replace('_', ' ')}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${getSeverityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                        <span className="text-xs text-gray-400">{task.department.toUpperCase()}</span>
                      </div>
                      <h3 className="font-semibold text-gray-900">{task.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                        <span>Assigned: {task.assigned_to}</span>
                        {task.due_date && <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <select
                        value={task.status}
                        onChange={(e) => handleUpdateTask(task.task_id, { status: e.target.value })}
                        className="text-xs px-2 py-1 border border-gray-200 rounded"
                      >
                        <option value="pending">Pending</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                      </select>
                      <button
                        onClick={() => handleDeleteTask(task.task_id)}
                        className="p-2 hover:bg-red-50 rounded-lg text-red-500"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>

      {/* Create Gap Modal */}
      <Modal isOpen={showGapModal} onClose={() => setShowGapModal(false)} title="Create New Gap">
        <form onSubmit={handleCreateGap} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
            <select
              value={gapForm.department}
              onChange={(e) => setGapForm({ ...gapForm, department: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Select Department</option>
              {departments.map(d => (
                <option key={d} value={d}>{d.toUpperCase()}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              value={gapForm.title}
              onChange={(e) => setGapForm({ ...gapForm, title: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Gap title"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={gapForm.description}
              onChange={(e) => setGapForm({ ...gapForm, description: e.target.value })}
              required
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Describe the gap..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
              <select
                value={gapForm.severity}
                onChange={(e) => setGapForm({ ...gapForm, severity: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select
                value={gapForm.category}
                onChange={(e) => setGapForm({ ...gapForm, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="api">API</option>
                <option value="compliance">Compliance</option>
                <option value="data">Data</option>
                <option value="policy">Policy</option>
                <option value="security">Security</option>
                <option value="performance">Performance</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={() => setShowGapModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" className="flex-1 px-4 py-2 text-white rounded-lg hover:opacity-90" style={{ background: '#F47216' }}>
              Create Gap
            </button>
          </div>
        </form>
      </Modal>

      {/* Create Task Modal */}
      <Modal isOpen={showTaskModal} onClose={() => setShowTaskModal(false)} title="Create New Task">
        <form onSubmit={handleCreateTask} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
            <select
              value={taskForm.department}
              onChange={(e) => setTaskForm({ ...taskForm, department: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Select Department</option>
              {departments.map(d => (
                <option key={d} value={d}>{d.toUpperCase()}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              value={taskForm.title}
              onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Task title"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={taskForm.description}
              onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
              required
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Describe the task..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Assigned To</label>
            <input
              type="text"
              value={taskForm.assigned_to}
              onChange={(e) => setTaskForm({ ...taskForm, assigned_to: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="Agent or team name"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select
                value={taskForm.priority}
                onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <input
                type="date"
                value={taskForm.due_date}
                onChange={(e) => setTaskForm({ ...taskForm, due_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={() => setShowTaskModal(false)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" className="flex-1 px-4 py-2 text-white rounded-lg hover:opacity-90" style={{ background: '#F47216' }}>
              Create Task
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default GapsTasksManagement;
