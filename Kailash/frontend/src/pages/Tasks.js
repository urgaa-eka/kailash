import React, { useState } from 'react';
import { CheckSquare, Plus, User, Eye, Edit } from 'lucide-react';
import { Card, CardContent } from '../components/UI/card';
import { Button } from '../components/UI/button';
import { Badge } from '../components/UI/badge';
import './Tasks.css';

const Tasks = () => {
    const [filter, setFilter] = useState('all');
    const [tasks] = useState([
        { id: 1, title: 'System maintenance check', department: 'Operations', status: 'in-progress', priority: 'high', assignee: 'John Doe', dueDate: '2025-11-25' },
        { id: 2, title: 'Customer feedback analysis', department: 'Support', status: 'pending', priority: 'medium', assignee: 'Jane Smith', dueDate: '2025-11-26' },
        { id: 3, title: 'Update documentation', department: 'Engineering', status: 'completed', priority: 'low', assignee: 'Mike Johnson', dueDate: '2025-11-24' },
        { id: 4, title: 'Security audit review', department: 'Security', status: 'pending', priority: 'urgent', assignee: 'Sarah Williams', dueDate: '2025-11-23' },
        { id: 5, title: 'Performance optimization', department: 'Engineering', status: 'in-progress', priority: 'high', assignee: 'David Brown', dueDate: '2025-11-27' },
    ]);

    const getStatusVariant = (status) => {
        const variants = {
            'completed': 'success',
            'in-progress': 'info',
            'pending': 'warning',
            'cancelled': 'danger'
        };
        return variants[status] || 'default';
    };

    const getPriorityVariant = (priority) => {
        const variants = {
            'urgent': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'default'
        };
        return variants[priority] || 'default';
    };

    const filteredTasks = filter === 'all' ? tasks : tasks.filter(t => t.status === filter);

    return (
        <div className="tasks-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">
                        <CheckSquare size={28} strokeWidth={1.5} className="inline-icon" /> Tasks
                    </h1>
                    <p className="page-subtitle">Manage and track all organizational tasks</p>
                </div>
                <Button variant="primary" icon={Plus}>Create Task</Button>
            </div>

            <div className="tasks-filters">
                <button className={`filter-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
                    All Tasks
                </button>
                <button className={`filter-btn ${filter === 'pending' ? 'active' : ''}`} onClick={() => setFilter('pending')}>
                    Pending
                </button>
                <button className={`filter-btn ${filter === 'in-progress' ? 'active' : ''}`} onClick={() => setFilter('in-progress')}>
                    In Progress
                </button>
                <button className={`filter-btn ${filter === 'completed' ? 'active' : ''}`} onClick={() => setFilter('completed')}>
                    Completed
                </button>
            </div>

            <Card>
                <div className="tasks-table-wrapper">
                    <table className="tasks-table">
                        <thead>
                            <tr>
                                <th>Task</th>
                                <th>Department</th>
                                <th>Assignee</th>
                                <th>Priority</th>
                                <th>Status</th>
                                <th>Due Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredTasks.map((task) => (
                                <tr key={task.id}>
                                    <td className="task-title">{task.title}</td>
                                    <td>{task.department}</td>
                                    <td>
                                        <div className="assignee">
                                            <User size={16} strokeWidth={1.5} />
                                            <span>{task.assignee}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <Badge variant={getPriorityVariant(task.priority)}>
                                            {task.priority}
                                        </Badge>
                                    </td>
                                    <td>
                                        <Badge variant={getStatusVariant(task.status)}>
                                            {task.status}
                                        </Badge>
                                    </td>
                                    <td>{task.dueDate}</td>
                                    <td>
                                        <div className="table-actions">
                                            <Button variant="ghost" size="small" icon={Eye} />
                                            <Button variant="ghost" size="small" icon={Edit} />
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
};

export default Tasks;
