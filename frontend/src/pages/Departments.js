import React, { useState, useEffect } from 'react';
import { Users, Plus, Eye, Edit, Settings, Sparkles } from 'lucide-react';
import { Card, CardContent } from '../components/UI/card';
import { Button } from '../components/UI/button';
import { Badge } from '../components/UI/badge';
import { useToast } from '../context/ToastContext';
import DeityAvatar from '../components/DeityAvatar';
import DepartmentTag from '../components/DepartmentTag';
import '../styles/spiritual-theme.css';
import './Departments.css';

const Departments = () => {
    const [departments, setDepartments] = useState([]);
    const [loading, setLoading] = useState(true);
    const { showToast } = useToast();

    useEffect(() => {
        fetchDepartments();
    }, []);

    const fetchDepartments = async () => {
        setLoading(true);
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            setDepartments([
                { id: 1, name: 'Operations', lead: 'John Doe', members: 12, workload: 75, status: 'active' },
                { id: 2, name: 'Maintenance', lead: 'Jane Smith', members: 8, workload: 60, status: 'active' },
                { id: 3, name: 'Customer Support', lead: 'Mike Johnson', members: 15, workload: 85, status: 'active' },
                { id: 4, name: 'Analytics', lead: 'Sarah Williams', members: 6, workload: 45, status: 'active' },
                { id: 5, name: 'Engineering', lead: 'David Brown', members: 10, workload: 90, status: 'active' },
            ]);
        } catch (error) {
            showToast('Failed to load departments', 'error');
        } finally {
            setLoading(false);
        }
    };

    const getWorkloadColor = (workload) => {
        if (workload >= 80) return 'danger';
        if (workload >= 60) return 'warning';
        return 'success';
    };

    return (
        <div className="departments-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">
                        <Users size={28} strokeWidth={1.5} className="inline-icon" /> Departments
                    </h1>
                    <p className="page-subtitle">Manage and monitor all organizational departments</p>
                </div>
                <Button variant="primary" icon={Plus}>Add Department</Button>
            </div>

            <div className="departments-stats">
                <Card className="stat-card">
                    <div className="stat-content">
                        <div className="stat-icon blue">
                            <Users size={24} strokeWidth={1.5} />
                        </div>
                        <div>
                            <div className="stat-label">Total Departments</div>
                            <div className="stat-value">5</div>
                        </div>
                    </div>
                </Card>
                <Card className="stat-card">
                    <div className="stat-content">
                        <div className="stat-icon green">
                            <Users size={24} strokeWidth={1.5} />
                        </div>
                        <div>
                            <div className="stat-label">Total Members</div>
                            <div className="stat-value">51</div>
                        </div>
                    </div>
                </Card>
                <Card className="stat-card">
                    <div className="stat-content">
                        <div className="stat-icon yellow">
                            <Users size={24} strokeWidth={1.5} />
                        </div>
                        <div>
                            <div className="stat-label">Avg Workload</div>
                            <div className="stat-value">71%</div>
                        </div>
                    </div>
                </Card>
            </div>

            <div className="departments-grid">
                {loading ? (
                    <div className="loading-state">Loading departments...</div>
                ) : (
                    departments.map(dept => (
                        <Card key={dept.id} className="department-card">
                            <div className="department-header">
                                <h3 className="department-name">{dept.name}</h3>
                                <Badge variant={dept.status === 'active' ? 'success' : 'default'}>
                                    {dept.status}
                                </Badge>
                            </div>
                            <div className="department-info">
                                <div className="info-item">
                                    <span className="info-label">Department Lead:</span>
                                    <span className="info-value">{dept.lead}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Team Members:</span>
                                    <span className="info-value">{dept.members}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Current Workload:</span>
                                    <Badge variant={getWorkloadColor(dept.workload)}>
                                        {dept.workload}%
                                    </Badge>
                                </div>
                            </div>
                            <div className="department-actions">
                                <Button variant="ghost" size="small" icon={Eye}>View</Button>
                                <Button variant="ghost" size="small" icon={Edit}>Edit</Button>
                                <Button variant="ghost" size="small" icon={Settings}>Settings</Button>
                            </div>
                        </Card>
                    ))
                )}
            </div>
        </div>
    );
};

export default Departments;
