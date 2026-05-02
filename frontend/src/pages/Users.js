import React, { useState, useEffect } from 'react';
import { 
  Users as UsersIcon, Plus, Edit2, Trash2, Shield, 
  Search, Filter, X, CheckCircle, AlertCircle, Loader2 
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import './Users.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ROLE_COLORS = {
  super_admin: '#e53935',      // Red
  admin: '#8e24aa',            // Purple
  manager: '#1e88e5',          // Blue
  operator: '#43a047',         // Green
  viewer: '#757575'            // Grey
};

const Users = () => {
  const { token, user: currentUser } = useAuthStore();
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // Search and filter
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('create'); // 'create' or 'edit'
  const [selectedUser, setSelectedUser] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    email: '',
    kailash_code: '',
    full_name: '',
    password: '',
    role: 'viewer',
    is_2fa_enabled: false
  });

  // Available roles from RBAC
  const [availableRoles, setAvailableRoles] = useState([]);

  useEffect(() => {
    loadUsers();
    loadRoles();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [users, searchTerm, selectedRole]);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch(`${BACKEND_URL}/api/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You do not have permission to view users');
        }
        throw new Error('Failed to load users');
      }
      
      const data = await response.json();
      setUsers(data.users || []);
    } catch (err) {
      console.error('Error loading users:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const loadRoles = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/rbac/roles`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableRoles(data.roles || []);
      }
    } catch (err) {
      console.error('Error loading roles:', err);
    }
  };

  const filterUsers = () => {
    let filtered = [...users];
    
    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(u => 
        u.full_name?.toLowerCase().includes(term) ||
        u.email?.toLowerCase().includes(term) ||
        u.kailash_code?.toLowerCase().includes(term)
      );
    }
    
    // Role filter
    if (selectedRole !== 'all') {
      filtered = filtered.filter(u => u.role === selectedRole);
    }
    
    setFilteredUsers(filtered);
  };

  const handleCreateUser = () => {
    setModalMode('create');
    setFormData({
      email: '',
      kailash_code: '',
      full_name: '',
      password: '',
      role: 'viewer',
      is_2fa_enabled: false
    });
    setShowModal(true);
  };

  const handleEditUser = (user) => {
    // Check if trying to edit self
    if (user.id === currentUser.id) {
      setError('Cannot edit your own account');
      return;
    }
    
    setModalMode('edit');
    setSelectedUser(user);
    setFormData({
      email: user.email || '',
      kailash_code: user.kailash_code || '',
      full_name: user.full_name || '',
      password: '',
      role: user.role || 'viewer',
      is_2fa_enabled: user.is_2fa_enabled || false
    });
    setShowModal(true);
  };

  const handleDeleteUser = async (user) => {
    // Prevent deleting self
    if (user.id === currentUser.id) {
      setError('Cannot delete your own account');
      return;
    }
    
    if (!window.confirm(`Delete user ${user.full_name}? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/users/${user.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You do not have permission to delete users');
        }
        throw new Error('Failed to delete user');
      }

      setSuccessMessage('User deleted successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
      await loadUsers();
    } catch (err) {
      console.error('Error deleting user:', err);
      setError(err.message);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const url = modalMode === 'create' 
        ? `${BACKEND_URL}/api/users`
        : `${BACKEND_URL}/api/users/${selectedUser.id}`;
      
      const method = modalMode === 'create' ? 'POST' : 'PATCH';
      
      const payload = { ...formData };
      // Don't send password if empty in edit mode
      if (modalMode === 'edit' && !payload.password) {
        delete payload.password;
      }

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You do not have permission to perform this action');
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Operation failed');
      }

      setSuccessMessage(modalMode === 'create' ? 'User created successfully' : 'User updated successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
      setShowModal(false);
      await loadUsers();
    } catch (err) {
      console.error('Error saving user:', err);
      setError(err.message);
      setTimeout(() => setError(null), 5000);
    }
  };

  const getRoleBadgeColor = (role) => {
    return ROLE_COLORS[role] || ROLE_COLORS.viewer;
  };

  return (
    <div className="users-container">
      <div className="users-header">
        <div className="header-left">
          <h1>
            <UsersIcon size={28} />
            User Management
          </h1>
          <p className="users-subtitle">Manage users and their roles with RBAC</p>
        </div>
        <button className="btn-create-user" onClick={handleCreateUser}>
          <Plus size={20} />
          Add User
        </button>
      </div>

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="alert alert-success">
          <CheckCircle size={18} />
          {successMessage}
        </div>
      )}
      
      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* Search and Filter Bar */}
      <div className="users-toolbar">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search by name, email, or Kailash Code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="filter-box">
          <Filter size={18} />
          <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
            <option value="all">All Roles</option>
            {availableRoles.map(role => (
              <option key={role.name} value={role.name}>{role.description}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="users-table-container">
        {isLoading ? (
          <div className="loading-state">
            <Loader2 className="spin" size={48} />
            <p>Loading users...</p>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="empty-state">
            <UsersIcon size={64} />
            <p>No users found</p>
            {searchTerm || selectedRole !== 'all' ? (
              <button className="btn-clear-filters" onClick={() => {
                setSearchTerm('');
                setSelectedRole('all');
              }}>
                Clear filters
              </button>
            ) : null}
          </div>
        ) : (
          <table className="users-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Kailash Code</th>
                <th>Role</th>
                <th>2FA Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map(user => (
                <tr key={user.id}>
                  <td>
                    <div className="user-name">
                      {user.full_name || 'N/A'}
                      {user.id === currentUser.id && (
                        <span className="badge-you">You</span>
                      )}
                    </div>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <code className="kailash-code">{user.kailash_code}</code>
                  </td>
                  <td>
                    <span 
                      className="role-badge" 
                      style={{ 
                        background: getRoleBadgeColor(user.role),
                        color: 'white'
                      }}
                    >
                      {user.role?.replace('_', ' ').toUpperCase() || 'VIEWER'}
                    </span>
                  </td>
                  <td>
                    {user.is_2fa_enabled ? (
                      <span className="status-badge status-enabled">
                        <Shield size={14} />
                        Enabled
                      </span>
                    ) : (
                      <span className="status-badge status-disabled">
                        Disabled
                      </span>
                    )}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn-icon btn-edit"
                        onClick={() => handleEditUser(user)}
                        title="Edit user"
                        disabled={user.id === currentUser.id}
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        className="btn-icon btn-delete"
                        onClick={() => handleDeleteUser(user)}
                        title="Delete user"
                        disabled={user.id === currentUser.id}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{modalMode === 'create' ? 'Create New User' : 'Edit User'}</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="user-form">
              <div className="form-group">
                <label>Full Name *</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                  disabled={modalMode === 'edit'}
                />
              </div>

              <div className="form-group">
                <label>Kailash Code *</label>
                <input
                  type="text"
                  value={formData.kailash_code}
                  onChange={(e) => setFormData({...formData, kailash_code: e.target.value})}
                  required
                  disabled={modalMode === 'edit'}
                />
              </div>

              <div className="form-group">
                <label>Password {modalMode === 'create' && '*'}</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required={modalMode === 'create'}
                  placeholder={modalMode === 'edit' ? 'Leave empty to keep current password' : ''}
                />
              </div>

              <div className="form-group">
                <label>Role *</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  required
                >
                  {availableRoles.map(role => (
                    <option key={role.name} value={role.name}>
                      {role.description}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-actions">
                <button type="button" className="btn-cancel" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-submit">
                  {modalMode === 'create' ? 'Create User' : 'Update User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
