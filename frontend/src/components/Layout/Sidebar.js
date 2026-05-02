import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Layers, 
  Cpu, 
  Users, 
  CheckSquare, 
  BarChart3, 
  FileText, 
  Settings, 
  ShieldCheck, 
  User,
  MessageCircle,
  Zap,
  Shield,
  Car
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose }) => {
    const location = useLocation();

    // KAILASH IS the operating system - navigation items
    const navItems = [
        { path: '/kailash', icon: LayoutDashboard, label: 'KAILASH Command' },
        { path: '/chat', icon: MessageCircle, label: 'Chat (GANESHA)' },
        { path: '/ganesha', icon: Cpu, label: 'GANESHA AI' },
        { path: '/departments', icon: Users, label: 'Departments' },
        { path: '/guardians', icon: Shield, label: 'Guardians' },
        { path: '/users', icon: Users, label: 'Users' },
        { path: '/urjaa', icon: Zap, label: 'URJAA EV' },
        { path: '/automobile', icon: Car, label: 'Automobile Pricing' },
        { path: '/tasks', icon: CheckSquare, label: 'Tasks' },
        { path: '/analytics', icon: BarChart3, label: 'Analytics' },
        { path: '/reports', icon: FileText, label: 'Reports' },
        { path: '/settings', icon: Settings, label: 'Settings' },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <>
            {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
            <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <ShieldCheck size={24} strokeWidth={1.5} />
                    <span>Kailash</span>
                </div>
                <nav className="sidebar-nav">
                    <ul className="nav-menu">
                        {navItems.map((item) => {
                            const IconComponent = item.icon;
                            return (
                                <li className="nav-item" key={item.path}>
                                    <Link 
                                        to={item.path} 
                                        className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                                        onClick={onClose}
                                    >
                                        <IconComponent size={20} strokeWidth={1.5} />
                                        <span>{item.label}</span>
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </nav>
                <div className="sidebar-footer">
                    <div className="sidebar-user">
                        <User size={20} strokeWidth={1.5} />
                        <div className="user-info">
                            <div className="user-name">Admin User</div>
                            <div className="user-role">Administrator</div>
                        </div>
                    </div>
                    <div className="version-info">
                        <span className="version-label">Version</span>
                        <span className="version-number">v1.0.0</span>
                    </div>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;
