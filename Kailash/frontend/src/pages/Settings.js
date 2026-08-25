import React, { useState } from 'react';
import { Settings as SettingsIcon, User, Bell, Shield, Palette, Globe } from 'lucide-react';
import { Card, CardContent } from '../components/UI/card';
import { Button } from '../components/UI/button';
import './Settings.css';

const Settings = () => {
    const [activeTab, setActiveTab] = useState('profile');

    const tabs = [
        { id: 'profile', label: 'Profile', icon: User },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'security', label: 'Security', icon: Shield },
        { id: 'appearance', label: 'Appearance', icon: Palette },
        { id: 'preferences', label: 'Preferences', icon: Globe },
    ];

    return (
        <div className="settings-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">
                        <SettingsIcon size={28} strokeWidth={1.5} className="inline-icon" /> Settings
                    </h1>
                    <p className="page-subtitle">Manage your account and application preferences</p>
                </div>
            </div>

            <div className="settings-layout">
                <div className="settings-sidebar">
                    <nav className="settings-nav">
                        {tabs.map(tab => {
                            const IconComponent = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    className={`settings-nav-item ${activeTab === tab.id ? 'active' : ''}`}
                                    onClick={() => setActiveTab(tab.id)}
                                >
                                    <IconComponent size={20} strokeWidth={1.5} />
                                    <span>{tab.label}</span>
                                </button>
                            );
                        })}
                    </nav>
                </div>

                <div className="settings-content">
                    {activeTab === 'profile' && (
                        <Card title="Profile Settings">
                            <div className="settings-section">
                                <div className="form-group">
                                    <label className="form-label">Full Name</label>
                                    <input type="text" className="form-control" defaultValue="Admin User" />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Email Address</label>
                                    <input type="email" className="form-control" defaultValue="admin@Kailash.com" />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Kailash Code</label>
                                    <input type="text" className="form-control" defaultValue="<REDACTED_kailash_code>" disabled />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Role</label>
                                    <input type="text" className="form-control" defaultValue="Administrator" disabled />
                                </div>
                                <div className="form-actions">
                                    <Button variant="primary">Save Changes</Button>
                                    <Button variant="secondary">Cancel</Button>
                                </div>
                            </div>
                        </Card>
                    )}

                    {activeTab === 'notifications' && (
                        <Card title="Notification Preferences">
                            <div className="settings-section">
                                <div className="setting-item">
                                    <div>
                                        <h4>Task Updates</h4>
                                        <p>Receive notifications when tasks are assigned or completed</p>
                                    </div>
                                    <input type="checkbox" defaultChecked />
                                </div>
                                <div className="setting-item">
                                    <div>
                                        <h4>System Alerts</h4>
                                        <p>Get notified about system maintenance and updates</p>
                                    </div>
                                    <input type="checkbox" defaultChecked />
                                </div>
                                <div className="setting-item">
                                    <div>
                                        <h4>Email Notifications</h4>
                                        <p>Receive email summaries of daily activities</p>
                                    </div>
                                    <input type="checkbox" />
                                </div>
                                <div className="form-actions">
                                    <Button variant="primary">Save Preferences</Button>
                                </div>
                            </div>
                        </Card>
                    )}

                    {activeTab === 'security' && (
                        <Card title="Security Settings">
                            <div className="settings-section">
                                <div className="form-group">
                                    <label className="form-label">Current Password</label>
                                    <input type="password" className="form-control" />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">New Password</label>
                                    <input type="password" className="form-control" />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Confirm New Password</label>
                                    <input type="password" className="form-control" />
                                </div>
                                <div className="form-actions">
                                    <Button variant="primary">Update Password</Button>
                                </div>
                            </div>
                        </Card>
                    )}

                    {activeTab === 'appearance' && (
                        <Card title="Appearance Settings">
                            <div className="settings-section">
                                <div className="setting-item">
                                    <div>
                                        <h4>Theme</h4>
                                        <p>Choose between light and dark mode</p>
                                    </div>
                                    <select className="form-control" style={{width: 'auto'}}>
                                        <option>Light</option>
                                        <option>Dark</option>
                                        <option>Auto</option>
                                    </select>
                                </div>
                                <div className="setting-item">
                                    <div>
                                        <h4>Compact Mode</h4>
                                        <p>Reduce spacing for more content visibility</p>
                                    </div>
                                    <input type="checkbox" />
                                </div>
                                <div className="form-actions">
                                    <Button variant="primary">Save Appearance</Button>
                                </div>
                            </div>
                        </Card>
                    )}

                    {activeTab === 'preferences' && (
                        <Card title="General Preferences">
                            <div className="settings-section">
                                <div className="form-group">
                                    <label className="form-label">Language</label>
                                    <select className="form-control">
                                        <option>English</option>
                                        <option>Hindi</option>
                                        <option>Spanish</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Timezone</label>
                                    <select className="form-control">
                                        <option>Asia/Kolkata (IST)</option>
                                        <option>America/New_York (EST)</option>
                                        <option>Europe/London (GMT)</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Date Format</label>
                                    <select className="form-control">
                                        <option>DD/MM/YYYY</option>
                                        <option>MM/DD/YYYY</option>
                                        <option>YYYY-MM-DD</option>
                                    </select>
                                </div>
                                <div className="form-actions">
                                    <Button variant="primary">Save Preferences</Button>
                                </div>
                            </div>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Settings;
