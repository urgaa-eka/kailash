import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Menu, X, ArrowLeft, LogOut, Home, Grid3X3 } from 'lucide-react';

const AppLayout = ({ children, showBackButton = false, showMenuButton = true, title = "Kailash" }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const handleBack = () => {
    // /kailash is now the main landing page after login, so go back in history
    navigate(-1);
  };

  // KAILASH IS the operating system - no separate apps
  const menuItems = [
    { label: 'KAILASH Command', path: '/kailash', icon: Home },
    { label: 'GANESHA Chat', path: '/ganesha', icon: null },
    { label: 'Departments', path: '/departments', icon: null },
    { label: 'Guardians', path: '/guardians', icon: null },
    { label: 'URJAA EV', path: '/urjaa', icon: null },
    { label: 'Analytics', path: '/analytics', icon: null },
    { label: 'Settings', path: '/settings', icon: null },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1E272E] via-[#222F3E] to-[#2C3E50]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#222F3E]/95 backdrop-blur-lg border-b border-white/10 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left Section */}
            <div className="flex items-center gap-3">
              {/* Back Button */}
              {showBackButton && (
                <button
                  onClick={handleBack}
                  className="p-2 rounded-lg bg-[#0A3D62]/30 hover:bg-[#0A3D62]/50 text-white transition-all duration-300 shadow-md hover:shadow-lg"
                  title="Go Back"
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
              )}

              {/* Menu Button */}
              {showMenuButton && (
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="p-2 rounded-lg bg-[#0A3D62]/30 hover:bg-[#0A3D62]/50 text-white transition-all duration-300 shadow-md hover:shadow-lg"
                  title="Menu"
                >
                  {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>
              )}

              {/* Logo & Title */}
              <div className="flex items-center gap-3">
                <img 
                  src="/logo.png" 
                  alt="Go4Garage" 
                  className="h-10 w-auto"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
                <div>
                  <h1 className="text-lg font-bold text-white tracking-tight">{title}</h1>
                  <p className="text-xs text-[#8395A7] font-medium">Go4Garage Command Center</p>
                </div>
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-3">
              {/* User Info */}
              <div className="hidden sm:block text-right">
                <p className="text-sm font-semibold text-white">Welcome Back</p>
                <p className="text-xs text-[#8395A7]">Kailash: V20099774J</p>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-all duration-300 border border-red-400/30 shadow-md hover:shadow-lg font-medium text-sm"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>

        {/* Dropdown Menu */}
        {menuOpen && (
          <div className="absolute top-16 left-0 right-0 bg-[#222F3E]/98 backdrop-blur-lg border-b border-white/10 shadow-2xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <nav className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {menuItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  
                  return (
                    <button
                      key={item.path}
                      onClick={() => {
                        navigate(item.path);
                        setMenuOpen(false);
                      }}
                      className={`
                        flex items-center gap-3 px-4 py-3 rounded-lg
                        transition-all duration-300 text-left
                        ${
                          isActive
                            ? 'bg-[#0A3D62] text-white shadow-lg'
                            : 'bg-[#0A3D62]/20 text-[#8395A7] hover:bg-[#0A3D62]/40 hover:text-white'
                        }
                      `}
                    >
                      {Icon && <Icon className="w-5 h-5" />}
                      <span className="font-medium text-sm">{item.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-[#222F3E]/80 backdrop-blur-lg border-t border-white/10 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <p className="text-sm text-[#8395A7] font-medium">
              © 2024 Go4Garage Pvt Ltd. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <a href="/terms" className="text-sm text-[#8395A7] hover:text-white transition-colors font-medium">
                Terms
              </a>
              <a href="/privacy" className="text-sm text-[#8395A7] hover:text-white transition-colors font-medium">
                Privacy
              </a>
              <a href="mailto:cto@go4garage.in" className="text-sm text-[#8395A7] hover:text-white transition-colors font-medium">
                Support
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AppLayout;
