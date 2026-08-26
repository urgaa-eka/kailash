import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import './MainLayout.css';

const MainLayout = ({ children }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [darkMode, setDarkMode] = useState(false);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const toggleTheme = () => {
        setDarkMode(!darkMode);
        document.body.classList.toggle('dark-mode');
    };

    return (
        <div className="app-layout">
            <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            <main className="main-content">
                <Header 
                    onMenuToggle={toggleSidebar}
                    onThemeToggle={toggleTheme}
                    darkMode={darkMode}
                />
                <div className="content-wrapper">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default MainLayout;
