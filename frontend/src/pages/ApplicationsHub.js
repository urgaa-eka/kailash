import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, FileText, Zap, LayoutDashboard, Settings, TrendingUp } from 'lucide-react';
import AppLayout from '../components/AppLayout';

const ApplicationsHub = () => {
  const navigate = useNavigate();

  const applications = [
    {
      id: 'kailash',
      name: 'KAILASH Dashboard',
      description: 'AI-powered organizational management with 20 departments and GANESHA assistant',
      icon: LayoutDashboard,
      color: 'from-g4g-blue/20 to-cyan-500/20',
      borderColor: 'border-blue-400/50',
      route: '/kailash',
      status: 'active'
    },
    {
      id: 'gst',
      name: 'GST Website',
      description: 'Complete GST compliance and filing management system',
      icon: FileText,
      color: 'from-green-500/20 to-emerald-500/20',
      borderColor: 'border-green-400/50',
      route: '/gst',
      status: 'active'
    },
    {
      id: 'tattoos',
      name: 'Tattoos Go4Garage Tool',
      description: 'Vehicle diagnostics and service management platform',
      icon: Settings,
      color: 'from-purple-500/20 to-pink-500/20',
      borderColor: 'border-purple-400/50',
      route: '/tattoos',
      status: 'active'
    },
    {
      id: 'ignition',
      name: 'Ignition App',
      description: 'Fleet management and vehicle tracking solution',
      icon: Zap,
      color: 'from-orange-500/20 to-red-500/20',
      borderColor: 'border-orange-400/50',
      route: '/ignition',
      status: 'active'
    },
    {
      id: 'analytics',
      name: 'Business Analytics',
      description: 'Real-time insights and performance metrics across all platforms',
      icon: TrendingUp,
      color: 'from-indigo-500/20 to-g4g-blue/20',
      borderColor: 'border-indigo-400/50',
      route: '/analytics',
      status: 'coming-soon'
    },
    {
      id: 'admin',
      name: 'Admin Console',
      description: 'System configuration and user management',
      icon: Cpu,
      color: 'from-slate-500/20 to-gray-500/20',
      borderColor: 'border-slate-400/50',
      route: '/admin',
      status: 'coming-soon'
    }
  ];

  const handleApplicationClick = (app) => {
    if (app.status === 'active') {
      navigate(app.route);
    }
  };

  return (
    <AppLayout showBackButton={false} showMenuButton={false} title="Kailash">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4 tracking-tight drop-shadow-lg">
            Select Your Application
          </h2>
          <p className="text-lg text-[#8395A7] max-w-2xl mx-auto font-medium leading-relaxed">
            Access Go4Garage's suite of integrated business management tools. Choose an application below to get started.
          </p>
        </div>

        {/* Applications Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {applications.map((app) => {
            const Icon = app.icon;
            const isActive = app.status === 'active';
            
            return (
              <div
                key={app.id}
                onClick={() => handleApplicationClick(app)}
                className={`
                  relative group
                  bg-gradient-to-br ${app.color}
                  backdrop-blur-lg
                  border-2 ${app.borderColor}
                  rounded-2xl p-6
                  transition-all duration-300
                  shadow-xl
                  ${
                    isActive
                      ? 'cursor-pointer hover:scale-105 hover:shadow-2xl hover:shadow-g4g-blue/30'
                      : 'opacity-60 cursor-not-allowed'
                  }
                `}
              >
                {/* Status Badge */}
                {!isActive && (
                  <div className="absolute top-4 right-4">
                    <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 text-xs font-bold rounded-full border border-yellow-400/40 shadow-md">
                      Coming Soon
                    </span>
                  </div>
                )}

                {/* Icon */}
                <div
                  className={`
                    w-16 h-16 rounded-2xl
                    flex items-center justify-center
                    mb-4
                    ${isActive ? 'bg-white/10' : 'bg-white/5'}
                    ${isActive ? 'group-hover:bg-white/20' : ''}
                    transition-all duration-300
                    shadow-lg
                  `}
                >
                  <Icon className={`w-8 h-8 ${isActive ? 'text-white' : 'text-white/50'}`} />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-white mb-2 tracking-tight">
                  {app.name}
                </h3>
                <p className="text-sm text-[#8395A7] leading-relaxed font-medium">
                  {app.description}
                </p>

                {/* Hover Effect */}
                {isActive && (
                  <div className="mt-4 flex items-center gap-2 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span className="text-sm font-bold">Launch Application</span>
                    <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Info Section */}
        <div className="mt-12 p-6 bg-[#0A3D62]/20 border border-[#0A3D62]/50 rounded-xl shadow-xl">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-full bg-[#FFC312]/20 flex items-center justify-center flex-shrink-0 shadow-lg">
              <svg className="w-6 h-6 text-[#FFC312]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-lg font-bold text-white mb-2 tracking-tight">Need Help?</h4>
              <p className="text-sm text-[#8395A7] leading-relaxed font-medium">
                For technical support or assistance with any application, contact our support team at{' '}
                <a href="mailto:cto@go4garage.in" className="text-[#FFC312] hover:underline font-semibold">
                  cto@go4garage.in
                </a>
                {' '}or call{' '}
                <a href="tel:7820938629" className="text-[#FFC312] hover:underline font-semibold">
                  7820938629
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default ApplicationsHub;
