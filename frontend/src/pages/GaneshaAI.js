import React, { useState } from 'react';
import { Cpu, Send, CheckCircle, Check, LayoutDashboard, FileText, Wrench, AlertTriangle } from 'lucide-react';
import { useToast } from '../context/ToastContext';
import { Card, CardContent } from '../components/UI/card';
import { Button } from '../components/UI/button';
import { Badge } from '../components/UI/badge';
import './GaneshaAI.css';

const GaneshaAI = () => {
    const [command, setCommand] = useState('');
    const [priority, setPriority] = useState('medium');
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const { showToast } = useToast();

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!command.trim()) {
            showToast('Please enter a command', 'error');
            return;
        }

        setLoading(true);
        
        try {
            // Simulate API call for now
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            setResponse({
                status: 'success',
                department: 'operations',
                action: 'Task created successfully',
                breakdown: [
                    'Analyze current workflow',
                    'Identify optimization opportunities',
                    'Implement improvements'
                ]
            });
            
            showToast('Command processed successfully!', 'success');
        } catch (error) {
            showToast('Failed to process command', 'error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="ganesha-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">
                        <Cpu size={28} strokeWidth={1.5} className="inline-icon" /> GANESHA AI Command Center
                    </h1>
                    <p className="page-subtitle">
                        Natural language task orchestration powered by Claude AI
                    </p>
                </div>
                <Badge variant="success">Active</Badge>
            </div>

            <div className="ganesha-grid">
                <div className="ganesha-main">
                    <Card title="Command Input">
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label className="form-label">
                                    What would you like GANESHA to do?
                                </label>
                                <textarea
                                    className="form-control ganesha-input"
                                    rows="4"
                                    value={command}
                                    onChange={(e) => setCommand(e.target.value)}
                                    placeholder="Example: Check the status of all charging stations and identify any that need maintenance..."
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Priority Level</label>
                                <div className="priority-selector">
                                    {['low', 'medium', 'high', 'urgent'].map((p) => (
                                        <button
                                            key={p}
                                            type="button"
                                            className={`priority-btn ${priority === p ? 'active' : ''} priority-${p}`}
                                            onClick={() => setPriority(p)}
                                            disabled={loading}
                                        >
                                            {p.toUpperCase()}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="form-actions">
                                <Button
                                    type="submit"
                                    variant="primary"
                                    loading={loading}
                                    icon={Send}
                                >
                                    Process Command
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    onClick={() => { setCommand(''); setResponse(null); }}
                                    disabled={loading}
                                >
                                    Clear
                                </Button>
                            </div>
                        </form>
                    </Card>

                    {response && (
                        <Card title="GANESHA Response" className="response-card">
                            <div className="response-status">
                                <Badge variant="success">
                                    <CheckCircle size={16} strokeWidth={1.5} className="inline-icon" /> Processed
                                </Badge>
                                <span className="response-dept">
                                    Routed to: <strong>{response.department}</strong>
                                </span>
                            </div>

                            <div className="response-action">
                                <h3>Action Taken</h3>
                                <p>{response.action}</p>
                            </div>

                            {response.breakdown && (
                                <div className="response-breakdown">
                                    <h3>Task Breakdown</h3>
                                    <ul>
                                        {response.breakdown.map((task, idx) => (
                                            <li key={idx}>
                                                <Check size={16} strokeWidth={1.5} className="inline-icon" /> {task}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </Card>
                    )}
                </div>

                <div className="ganesha-sidebar">
                    <Card title="Quick Actions">
                        <div className="quick-actions">
                            <button 
                                className="quick-action-btn"
                                onClick={() => setCommand('Check all station statuses')}
                            >
                                <LayoutDashboard size={20} strokeWidth={1.5} />
                                <span>Station Status</span>
                            </button>
                            <button 
                                className="quick-action-btn"
                                onClick={() => setCommand('Generate weekly performance report')}
                            >
                                <FileText size={20} strokeWidth={1.5} />
                                <span>Performance Report</span>
                            </button>
                            <button 
                                className="quick-action-btn"
                                onClick={() => setCommand('Identify maintenance priorities')}
                            >
                                <Wrench size={20} strokeWidth={1.5} />
                                <span>Maintenance Check</span>
                            </button>
                            <button 
                                className="quick-action-btn"
                                onClick={() => setCommand('Review recent incidents')}
                            >
                                <AlertTriangle size={20} strokeWidth={1.5} />
                                <span>Incident Review</span>
                            </button>
                        </div>
                    </Card>

                    <Card title="Recent Commands">
                        <div className="recent-commands">
                            <div className="recent-command-item">
                                <div className="command-text">Check station health</div>
                                <div className="command-time">2h ago</div>
                            </div>
                            <div className="recent-command-item">
                                <div className="command-text">Generate report</div>
                                <div className="command-time">5h ago</div>
                            </div>
                            <div className="recent-command-item">
                                <div className="command-text">Assign maintenance tasks</div>
                                <div className="command-time">1d ago</div>
                            </div>
                        </div>
                    </Card>

                    <Card title="AI Statistics">
                        <div className="ai-stats">
                            <div className="stat-item">
                                <div className="stat-label">Commands Today</div>
                                <div className="stat-value">12</div>
                            </div>
                            <div className="stat-item">
                                <div className="stat-label">Success Rate</div>
                                <div className="stat-value">98%</div>
                            </div>
                            <div className="stat-item">
                                <div className="stat-label">Avg Response</div>
                                <div className="stat-value">2.3s</div>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default GaneshaAI;
