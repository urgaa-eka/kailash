import React, { useState } from 'react';
import { Search, Bell, Menu, User, LogOut, Settings, HelpCircle, Sun, Moon } from 'lucide-react';
import './Header.css';

const Header = ({ onMenuToggle }) => {
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [showHelp, setShowHelp] = useState(false);
    const [isDark, setIsDark] = useState(() => {
        return localStorage.getItem('theme') === 'dark';
    });
    const [showNotifications, setShowNotifications] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('token');
        window.location.href = '/';
    };

    const toggleTheme = () => {
        const newTheme = !isDark;
        setIsDark(newTheme);
        if (newTheme) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    };

    React.useEffect(() => {
        if (isDark) {
            document.documentElement.classList.add('dark');
        }
    }, []);

    return (
        <header className="header">
            <button className="menu-toggle" onClick={onMenuToggle}>
                <Menu size={24} strokeWidth={1.5} />
            </button>
            
            <div className="header-search">
                <Search size={20} strokeWidth={1.5} />
                <input type="text" placeholder="Search dashboard, tasks, users..." />
            </div>
            
            <div className="header-actions">
                <button className="header-btn" onClick={toggleTheme} title={isDark ? "Light Mode" : "Dark Mode"}>
                    {isDark ? <Sun size={20} strokeWidth={1.5} /> : <Moon size={20} strokeWidth={1.5} />}
                </button>

                <button className="header-btn" onClick={() => setShowHelp(!showHelp)} title="Help & Documentation">
                    <HelpCircle size={20} strokeWidth={1.5} />
                </button>
                
                <button className="header-btn notification-btn" onClick={() => setShowNotifications(!showNotifications)}>
                    <Bell size={20} strokeWidth={1.5} />
                    <span className="notification-badge">2</span>
                </button>
                
                <div className="user-menu">
                    <button className="user-avatar" onClick={() => setShowUserMenu(!showUserMenu)}>
                        <User size={20} strokeWidth={1.5} />
                    </button>
                    
                    {showUserMenu && (
                        <div className="user-dropdown">
                            <a href="/profile" className="dropdown-item">
                                <User size={16} strokeWidth={1.5} />
                                <span>My Profile</span>
                            </a>
                            <a href="/settings" className="dropdown-item">
                                <Settings size={16} strokeWidth={1.5} />
                                <span>Settings</span>
                            </a>
                            <button onClick={handleLogout} className="dropdown-item logout-btn">
                                <LogOut size={16} strokeWidth={1.5} />
                                <span>Logout</span>
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {showHelp && (
                <div className="help-modal">
                    <div className="help-overlay" onClick={() => setShowHelp(false)} />
                    <div className="help-drawer">
                        <div className="help-header">
                            <h2>Help & Documentation</h2>
                            <button onClick={() => setShowHelp(false)} className="close-btn">
                                ×
                            </button>
                        </div>
                        <div className="help-content">
                            <div className="help-section">
                                <h3>Quick Start Guide</h3>
                                <ul>
                                    <li>Navigate using the sidebar menu</li>
                                    <li>Use GANESHA AI for intelligent assistance</li>
                                    <li>Manage tasks and departments from respective pages</li>
                                </ul>
                            </div>
                            <div className="help-section">
                                <h3>Keyboard Shortcuts</h3>
                                <ul>
                                    <li><kbd>Ctrl/Cmd + K</kbd> - Global search</li>
                                    <li><kbd>G</kbd> then <kbd>D</kbd> - Go to Dashboard</li>
                                    <li><kbd>G</kbd> then <kbd>A</kbd> - Go to GANESHA AI</li>
                                </ul>
                            </div>
                            <div className="help-section">
                                <h3>Support</h3>
                                <p>Email: support@go4garage.com</p>
                                <p>Phone: +91 XXX-XXX-XXXX</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {showNotifications && (
                <div className="notifications-dropdown">
                    <div className="notifications-header">
                        <h3>Notifications</h3>
                        <span className="badge">2 New</span>
                    </div>
                    <div className="notifications-list">
                        <div className="notification-item unread">
                            <div className="notification-icon success">
                                <Bell size={16} />
                            </div>
                            <div className="notification-content">
                                <p className="notification-title">Task Completed</p>
                                <p className="notification-text">Fleet maintenance task has been completed</p>
                                <span className="notification-time">5 minutes ago</span>
                            </div>
                        </div>
                        <div className="notification-item unread">
                            <div className="notification-icon info">
                                <Bell size={16} />
                            </div>
                            <div className="notification-content">
                                <p className="notification-title">New Message</p>
                                <p className="notification-text">You have a new message from GANESHA AI</p>
                                <span className="notification-time">1 hour ago</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </header>
    );
};

export default Header;
