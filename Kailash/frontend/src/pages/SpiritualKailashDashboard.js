import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Briefcase, 
  Activity, 
  TrendingUp, 
  TrendingDown,
  Users, 
  Shield, 
  Heart,
  CheckCircle,
  ChevronRight,
  ChevronDown,
  Search,
  Bell,
  LogOut,
  Settings,
  Command,
  Zap,
  Target,
  BarChart3,
  Layers,
  Lock,
  Wifi,
  Database,
  Globe,
  X
} from 'lucide-react';
import { DEPARTMENTS } from '../data/departmentsData';
import { useAuthStore } from '../stores/authStore';
import DepartmentDetailsPanel from '../components/DepartmentDetailsPanel';
import '../styles/spiritual-theme.css';

// Spiritual Logo Component - Square Transparent HD
const SpiritualLogo = ({ size = 40, className = '' }) => (
  <div 
    className={`deity-avatar-wrapper ${className}`}
    style={{ 
      width: size, 
      height: size, 
      minWidth: size, 
      minHeight: size,
      background: 'transparent',
      borderRadius: '4px'
    }}
  >
    <img 
      src="https://customer-assets.emergentagent.com/job_mystic-ui-2/artifacts/ue6hdyaa_icon.png"
      alt="KAILASH Logo"
      className="deity-avatar-img"
      style={{ background: 'transparent', borderRadius: '4px' }}
    />
  </div>
);

// KPI Card Component
const KPICard = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'blue' }) => {
  const colorClasses = {
    blue: 'text-white',
    green: 'bg-green-50 text-green-600',
    amber: 'bg-amber-50 text-amber-600'
  };
  
  return (
    <div className="bg-white rounded-lg p-5 border border-gray-100 shadow-sm hover:shadow-md transition-all" style={{ borderTop: '3px solid #F47216' }}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <h3 className="text-3xl font-bold" style={{ color: '#0A3D62' }}>{value}</h3>
        </div>
        <div className={`p-3 rounded-lg ${color === 'blue' ? '' : colorClasses[color]}`} style={color === 'blue' ? { background: '#0A3D62' } : {}}>
          <Icon size={22} className={color === 'blue' ? 'text-white' : ''} />
        </div>
      </div>
      <div className="flex items-center gap-2">
        {trend && (
          <span className={`flex items-center gap-1 text-xs font-medium ${
            trend === 'up' ? 'text-green-600' : 'text-red-500'
          }`}>
            {trend === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {trendValue}
          </span>
        )}
        <span className="text-xs text-gray-500">{subtitle}</span>
      </div>
    </div>
  );
};

// Department List Item Component
const DepartmentItem = ({ department, isActive, onClick, onNavigate }) => (
  <button
    onClick={onClick}
    onDoubleClick={() => onNavigate && onNavigate(department)}
    className={`w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center gap-3 ${
      isActive 
        ? 'bg-orange-50 border-l-4' 
        : 'hover:bg-gray-50 border-l-4 border-transparent'
    }`}
    style={isActive ? { borderLeftColor: '#F47216' } : {}}
    title="Double-click to view details"
  >
    <SpiritualLogo size={36} />
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-sm truncate" style={{ color: '#0A3D62' }}>{department.name}</span>
        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
          department.workload > 80 ? 'bg-red-100 text-red-700' :
          department.workload > 70 ? 'text-white' :
          'bg-green-100 text-green-700'
        }`} style={department.workload > 70 && department.workload <= 80 ? { background: '#F47216' } : {}}>
          {department.workload}%
        </span>
      </div>
      <p className="text-xs text-gray-500 truncate">{department.role}</p>
    </div>
    <ChevronRight size={16} className={`text-gray-400 transition-transform ${
      isActive ? 'rotate-90' : ''
    }`} />
  </button>
);

// Security Layer Item
const SecurityLayer = ({ name, status, icon: Icon }) => (
  <div className="flex items-center justify-between py-2">
    <div className="flex items-center gap-2">
      <Icon size={14} className="text-white/70" />
      <span className="text-sm text-white/90">{name}</span>
    </div>
    <span className="px-2 py-0.5 rounded text-[10px] font-semibold text-white" style={{ background: 'rgba(244, 114, 22, 0.8)' }}>
      {status}
    </span>
  </div>
);

// Harmony Dimension Bar
const HarmonyBar = ({ name, score }) => (
  <div className="py-2">
    <div className="flex items-center justify-between mb-1">
      <span className="text-sm text-white/90">{name}</span>
      <span className="text-xs text-white/70">{score}%</span>
    </div>
    <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
      <div 
        className="h-full rounded-full transition-all duration-500"
        style={{ width: `${score}%`, background: '#F47216' }}
      />
    </div>
  </div>
);

const SpiritualKailashDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [showGaneshaModal, setShowGaneshaModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard' or 'departments'
  const [currentSloka, setCurrentSloka] = useState(0);

  // Bhagavad Gita Slokas - Hindi with English meaning
  const gitaSlokas = [
    {
      hindi: "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
      english: "You have the right to work only, but never to its fruits."
    },
    {
      hindi: "योगः कर्मसु कौशलम्।",
      english: "Excellence in action is Yoga."
    },
    {
      hindi: "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।",
      english: "Elevate yourself through your own efforts; do not degrade yourself."
    },
    {
      hindi: "मन एव मनुष्याणां कारणं बन्धमोक्षयोः।",
      english: "The mind alone is the cause of bondage and liberation."
    },
    {
      hindi: "श्रद्धावान् लभते ज्ञानम्।",
      english: "One who has faith attains knowledge."
    },
    {
      hindi: "समत्वं योग उच्यते।",
      english: "Equanimity of mind is called Yoga."
    },
    {
      hindi: "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।",
      english: "Whenever there is decline of righteousness, I manifest myself."
    },
    {
      hindi: "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।",
      english: "Abandon all duties and surrender unto Me alone."
    }
  ];

  // Rotate sloka every 15 minutes
  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSloka((prev) => (prev + 1) % gitaSlokas.length);
    }, 15 * 60 * 1000); // 15 minutes

    return () => clearInterval(interval);
  }, [gitaSlokas.length]);

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const kpiData = {
    departments: 20,
    activeTasks: 127,
    tasksTrend: '+12%',
    completedToday: 45,
    harmonyScore: 92
  };

  // SHIV Guardian Data - Problems Resolved
  const shivData = {
    mode: 'Meditation',
    systemHealth: 98,
    threatsBlocked: 47,
    autoResolved: 23,
    productMetrics: {
      URGAA: { 
        chargersRectified: 12, 
        newSitesFound: 3, 
        uptimeRestored: 99.2,
        apiErrors: 0
      },
      GSTSAAS: { 
        filingErrors: 5, 
        dataSync: 100,
        deadlinesManaged: 8,
        complianceScore: 98
      },
      IGNITION: { 
        crashesFixed: 7, 
        performanceBoost: 15,
        securityPatches: 3,
        uptimeScore: 99.8
      }
    }
  };

  // PARVATI Harmony Data - Internal Growth
  const parvatiData = {
    harmonyScore: 92,
    trend: 'improving',
    productMetrics: {
      URGAA: { 
        revenueGrowth: '+18%', 
        activeStations: 847,
        sessionsToday: 1234,
        newUsers: 45
      },
      GSTSAAS: { 
        clientGrowth: '+12%', 
        workshopsActive: 156,
        returnsFiled: 89,
        satisfactionScore: 4.6
      },
      IGNITION: { 
        userGrowth: '+22%', 
        activeDrivers: 2341,
        tripsCompleted: 567,
        appRating: 4.8
      }
    }
  };

  const shivLayers = [
    { name: 'Authentication', status: 'Active', icon: Lock },
    { name: 'API Health', status: 'Active', icon: Wifi },
    { name: 'System Load', status: 'Active', icon: Activity },
    { name: 'Data Integrity', status: 'Active', icon: Database },
    { name: 'Network Security', status: 'Active', icon: Globe }
  ];

  const harmonyDimensions = [
    { name: 'Task Distribution', score: 90 },
    { name: 'Agent Utilization', score: 88 },
    { name: 'Response Time', score: 92 }
  ];

  const filteredDepartments = DEPARTMENTS.filter(dept =>
    dept.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    dept.role.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const dailyQuote = {
    text: "In stillness lies infinite power.",
    source: "Patanjali Yoga Sutras"
  };

  return (
    <div className="min-h-screen lotus-bg" style={{ background: '#ffffff' }}>
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 fixed top-0 left-0 right-0 z-50" style={{ borderBottomColor: '#F47216', borderBottomWidth: '2px' }}>
        <div className="flex items-center justify-between max-w-[1920px] mx-auto">
          {/* Logo */}
          <div className="flex items-center gap-4">
            <SpiritualLogo size={44} />
            <div>
              <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#0A3D62' }}>KAILASH</h1>
              <p className="text-xs text-gray-500 flex items-center gap-2">
                Command Center
                <span className="meditation-indicator" style={{ background: '#F47216' }} />
              </p>
            </div>
          </div>

          {/* Search */}
          <div className="flex-1 max-w-md mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search departments, tasks..."
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-400 transition-all"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {/* NEW: Executive Dashboard Link */}
            <button
              onClick={() => navigate('/dashboard/executive')}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg transition-all hover:bg-blue-700 flex items-center gap-2"
            >
              <BarChart3 size={16} />
              Executive View
            </button>
            
            {/* Knowledge Base */}
            <button
              onClick={() => navigate('/knowledge-base')}
              className="px-4 py-2 bg-purple-600 text-white text-sm font-semibold rounded-lg transition-all hover:bg-purple-700 flex items-center gap-2"
            >
              <Database size={16} />
              RAG KB
            </button>
            
            {/* Gap & Task Management */}
            <button
              onClick={() => navigate('/management')}
              className="px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg transition-all hover:bg-green-700 flex items-center gap-2"
            >
              <Target size={16} />
              Manage
            </button>
            
            {/* NEW: GANESHA Chat Link */}
            <button
              onClick={() => navigate('/ganesha-chat')}
              className="px-4 py-2 text-white text-sm font-semibold rounded-lg transition-all shadow-lg flex items-center gap-2 hover:opacity-90"
              style={{ background: '#F47216' }}
            >
              <Zap size={16} />
              GANESHA AI
            </button>
            
            <button
              onClick={() => setShowGaneshaModal(true)}
              className="px-5 py-2.5 text-white text-sm font-semibold rounded-lg transition-all shadow-lg flex items-center gap-2 hover:opacity-90"
              style={{ background: '#0A3D62' }}
            >
              <Command size={16} />
              GANESHA
            </button>
            
            <button className="relative p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {/* User Profile with Dropdown */}
            <div className="relative">
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-3 pl-3 border-l border-gray-200 hover:bg-gray-50 rounded-lg py-1 pr-2 transition-all"
              >
                <SpiritualLogo size={36} />
                <div className="hidden md:block text-left">
                  <p className="text-sm font-semibold text-gray-900">{user?.full_name || 'Vivek Gupta'}</p>
                  <p className="text-xs text-gray-500">{user?.department || 'Chief Executive Officer'}</p>
                </div>
                <ChevronDown size={16} className={`text-gray-400 transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
              </button>
              
              {showUserMenu && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl border border-gray-200 shadow-xl z-50 overflow-hidden">
                  <div className="p-4 border-b border-gray-100 bg-gray-50">
                    <p className="font-semibold text-gray-900">{user?.full_name || 'Vivek Gupta'}</p>
                    <p className="text-xs text-gray-500">{user?.email || 'vivek@kailash.ai'}</p>
                    <p className="text-xs text-orange-600 font-medium mt-1">Kailash: {user?.kailash_code || '<REDACTED_kailash_code>'}</p>
                  </div>
                  <div className="p-2">
                    <button 
                      onClick={() => { navigate('/dashboard/executive'); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors text-sm"
                    >
                      <BarChart3 size={16} />
                      Executive Dashboard
                    </button>
                    <button 
                      onClick={() => { navigate('/settings'); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors text-sm"
                    >
                      <Settings size={16} />
                      Settings
                    </button>
                    <div className="border-t border-gray-100 my-2"></div>
                    <button 
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm"
                    >
                      <LogOut size={16} />
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="flex pt-20">
        {/* Sidebar */}
        <aside className="fixed left-0 top-20 bottom-0 w-80 bg-white border-r border-gray-100 overflow-hidden flex flex-col">
          {/* View Toggle */}
          <div className="p-4 border-b border-gray-100">
            <div className="flex gap-2 mb-3">
              <button
                onClick={() => setActiveView('dashboard')}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeView === 'dashboard' 
                    ? 'text-white' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                style={activeView === 'dashboard' ? { background: '#0A3D62' } : {}}
              >
                <BarChart3 size={16} />
                Dashboard
              </button>
              <button
                onClick={() => setActiveView('departments')}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeView === 'departments' 
                    ? 'text-white' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                style={activeView === 'departments' ? { background: '#0A3D62' } : {}}
              >
                <Layers size={16} />
                Departments
              </button>
            </div>
            
            {activeView === 'departments' && (
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Filter departments..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-400"
                />
              </div>
            )}
          </div>
          
          {/* Sidebar Content */}
          {activeView === 'departments' ? (
            <div className="p-4 flex-1 overflow-y-auto">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Departments</h2>
                <span className="text-xs text-gray-500">{filteredDepartments.length} teams</span>
              </div>
              <div className="space-y-1">
                {filteredDepartments.map(dept => (
                  <DepartmentItem 
                    key={dept.id}
                    department={dept}
                    isActive={selectedDepartment?.id === dept.id}
                    onClick={() => setSelectedDepartment(dept)}
                    onNavigate={(d) => navigate(`/department/${d.id}`)}
                  />
                ))}
              </div>
            </div>
          ) : (
            /* Dashboard Summary View with Gita Sloka */
            <div className="flex-1 overflow-hidden p-3 flex flex-col">
              {/* SHIV Guardian Summary */}
              <div className="rounded-lg p-3 mb-3" style={{ background: '#0A3D62' }}>
                <div className="flex items-center gap-2 mb-2">
                  <Shield size={16} className="text-white" />
                  <span className="text-white font-bold text-sm">SHIV Guardian</span>
                  <span className="ml-auto px-2 py-0.5 rounded text-[10px] font-bold bg-green-500 text-white">
                    {shivData.mode}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="bg-white/10 rounded p-2">
                    <div className="text-white/70">System Health</div>
                    <div className="text-white font-bold">{shivData.systemHealth}%</div>
                  </div>
                  <div className="bg-white/10 rounded p-2">
                    <div className="text-white/70">Auto Resolved</div>
                    <div className="text-white font-bold">{shivData.autoResolved}</div>
                  </div>
                </div>
              </div>

              {/* PARVATI Harmony Summary */}
              <div className="rounded-lg p-3 mb-3" style={{ background: '#F47216' }}>
                <div className="flex items-center gap-2 mb-2">
                  <Heart size={16} className="text-gray-900" />
                  <span className="text-gray-900 font-bold text-sm">PARVATI Harmony</span>
                  <span className="ml-auto px-2 py-0.5 rounded text-[10px] font-bold bg-gray-900 text-white">
                    {parvatiData.harmonyScore}%
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-1">
                  {harmonyDimensions.map((dim, i) => (
                    <div key={i} className="bg-white/90 rounded p-1.5 text-center">
                      <div className="text-gray-600 text-[9px]">{dim.name.split(' ')[0]}</div>
                      <div className="text-gray-900 font-bold text-xs">{dim.score}%</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sloka Section - White background with icon */}
              <div className="flex-1 rounded-lg p-4 border border-gray-200 flex flex-col items-center justify-center text-center bg-white shadow-sm">
                {/* Icon from uploaded image */}
                <img 
                  src="https://customer-assets.emergentagent.com/job_f1db44a4-1880-4018-83d2-173938898a8b/artifacts/hyj4nah3_icon.png" 
                  alt="Spiritual Icon" 
                  className="w-16 h-16 mb-4"
                />
                
                {/* Hindi Sloka - Bold */}
                <p className="text-base font-bold mb-3 leading-relaxed text-gray-900">
                  {gitaSlokas[currentSloka].hindi}
                </p>
                
                {/* English Translation - Bold */}
                <p className="text-sm font-bold text-gray-800 leading-relaxed">
                  {gitaSlokas[currentSloka].english}
                </p>
              </div>
            </div>
          )}
        </aside>

        {/* Main Content - No Scroll */}
        <main className="flex-1 ml-80 p-4 h-[calc(100vh-80px)] overflow-hidden">
          {/* Show Department Details Panel when department selected */}
          {selectedDepartment && activeView === 'departments' ? (
            <div className="h-full overflow-y-auto">
              <DepartmentDetailsPanel 
                department={selectedDepartment} 
                onClose={() => setSelectedDepartment(null)} 
              />
            </div>
          ) : (
            <>
          {/* Quote Banner - Compact */}
          <div className="rounded-lg p-2 mb-3 text-white" style={{ background: '#0A3D62' }}>
            <p className="text-white/95 font-medium text-sm">&ldquo;{dailyQuote.text}&rdquo; <span className="text-white/70 text-xs">— {dailyQuote.source}</span></p>
          </div>

          {/* KPI Grid - Compact */}
          <div className="grid grid-cols-4 gap-3 mb-3">
            <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <Briefcase size={16} style={{ color: '#0A3D62' }} />
                <span className="text-xs text-gray-500">Departments</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{kpiData.departments}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <Activity size={16} style={{ color: '#F47216' }} />
                <span className="text-xs text-gray-500">Active Tasks</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{kpiData.activeTasks} <span className="text-xs text-green-500">{kpiData.tasksTrend}</span></div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle size={16} className="text-green-500" />
                <span className="text-xs text-gray-500">Completed</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{kpiData.completedToday}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <Heart size={16} style={{ color: '#F47216' }} />
                <span className="text-xs text-gray-500">Harmony</span>
              </div>
              <div className="text-2xl font-bold" style={{ color: '#0A3D62' }}>{kpiData.harmonyScore}%</div>
            </div>
          </div>

          {/* Guardian Panels - Compact Side by Side */}
          <div className="grid grid-cols-2 gap-3 mb-3">
            {/* SHIV Guardian - Compact */}
            <div className="rounded-lg p-4 text-white" style={{ background: '#0A3D62' }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: '#F47216' }}>
                  <Shield size={20} className="text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-sm">SHIV Guardian</h3>
                  <p className="text-[10px] text-white/70">Security & Protection</p>
                </div>
                <span className="ml-auto px-2 py-0.5 rounded text-[10px] font-bold bg-green-500 text-white">Active</span>
              </div>
              <div className="grid grid-cols-5 gap-1">
                {shivLayers.map((layer, idx) => (
                  <div key={idx} className="bg-white/10 rounded p-1.5 text-center">
                    <layer.icon size={12} className="mx-auto text-white/70 mb-0.5" />
                    <div className="text-[8px] text-white/60 truncate">{layer.name.split(' ')[0]}</div>
                    <div className="text-[9px] font-bold" style={{ color: '#F47216' }}>{layer.status}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* PARVATI Harmony - Compact */}
            <div className="rounded-lg p-4 text-white" style={{ background: '#0A3D62' }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: '#F47216' }}>
                  <Heart size={20} className="text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-sm">PARVATI Harmony</h3>
                  <p className="text-[10px] text-white/70">Workload Balance</p>
                </div>
                <span className="ml-auto px-2 py-0.5 rounded text-[10px] font-bold" style={{ background: '#F47216' }}>{kpiData.harmonyScore}%</span>
              </div>
              <div className="space-y-1.5">
                {harmonyDimensions.map((dim, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-[10px] text-white/70 w-20">{dim.name}</span>
                    <div className="flex-1 h-1.5 bg-white/20 rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${dim.score}%`, background: '#F47216' }} />
                    </div>
                    <span className="text-[10px] font-bold w-8">{dim.score}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Products Summary - Horizontal Black Cards with AI Tasks */}
          <div className="grid grid-cols-3 gap-3">
            {/* URGAA - EV Charging */}
            <div className="rounded-lg p-3" style={{ background: '#1a1a2e' }}>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-lg bg-yellow-500 flex items-center justify-center">
                  <Zap size={16} className="text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">URGAA</h3>
                  <p className="text-[10px] text-gray-400">EV Charging Network</p>
                </div>
              </div>
              
              {/* AI Tasks Summary */}
              <div className="space-y-2 mb-3">
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Auto-diagnosed 12 faulty chargers</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Optimized pricing for 847 stations</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Predicted maintenance for 23 units</span>
                </div>
              </div>
              
              {/* Metrics */}
              <div className="grid grid-cols-4 gap-1 text-center">
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-white font-bold text-sm">847</div>
                  <div className="text-gray-400 text-[8px]">Stations</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-white font-bold text-sm">12</div>
                  <div className="text-gray-400 text-[8px]">Fixed</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-green-400 font-bold text-sm">99.2%</div>
                  <div className="text-gray-400 text-[8px]">Uptime</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-green-400 font-bold text-sm">+18%</div>
                  <div className="text-gray-400 text-[8px]">Revenue</div>
                </div>
              </div>
            </div>

            {/* GSTSAAS - GST Compliance */}
            <div className="rounded-lg p-3" style={{ background: '#1a1a2e' }}>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                  <Briefcase size={16} className="text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">GSTSAAS</h3>
                  <p className="text-[10px] text-gray-400">GST Compliance Platform</p>
                </div>
              </div>
              
              {/* AI Tasks Summary */}
              <div className="space-y-2 mb-3">
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Auto-filed 89 GST returns today</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Detected 5 filing errors, corrected</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Sent 156 deadline reminders</span>
                </div>
              </div>
              
              {/* Metrics */}
              <div className="grid grid-cols-4 gap-1 text-center">
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-white font-bold text-sm">156</div>
                  <div className="text-gray-400 text-[8px]">Workshops</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-white font-bold text-sm">89</div>
                  <div className="text-gray-400 text-[8px]">Returns</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-green-400 font-bold text-sm">98%</div>
                  <div className="text-gray-400 text-[8px]">Compliance</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-green-400 font-bold text-sm">+12%</div>
                  <div className="text-gray-400 text-[8px]">Growth</div>
                </div>
              </div>
            </div>

            {/* IGNITION - Driver App */}
            <div className="rounded-lg p-3" style={{ background: '#1a1a2e' }}>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
                  <Target size={16} className="text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">IGNITION</h3>
                  <p className="text-[10px] text-gray-400">Driver Application</p>
                </div>
              </div>
              
              {/* AI Tasks Summary */}
              <div className="space-y-2 mb-3">
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Resolved 7 app crashes automatically</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Optimized routes for 567 trips</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <CheckCircle size={12} className="text-green-400" />
                  <span className="text-gray-300">Pushed 3 security patches live</span>
                </div>
              </div>
              
              {/* Metrics */}
              <div className="grid grid-cols-4 gap-1 text-center">
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-white font-bold text-sm">2341</div>
                  <div className="text-gray-400 text-[8px]">Drivers</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-white font-bold text-sm">567</div>
                  <div className="text-gray-400 text-[8px]">Trips</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-green-400 font-bold text-sm">99.8%</div>
                  <div className="text-gray-400 text-[8px]">Uptime</div>
                </div>
                <div className="bg-white/10 rounded p-1.5">
                  <div className="text-green-400 font-bold text-sm">+22%</div>
                  <div className="text-gray-400 text-[8px]">Growth</div>
                </div>
              </div>
            </div>
          </div>
            </>
          )}
        </main>
      </div>

      {/* GANESHA Command Modal */}
      {showGaneshaModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-6">
          <div className="bg-white rounded-lg shadow-2xl max-w-xl w-full overflow-hidden">
            <div className="p-6 text-white" style={{ background: '#0A3D62' }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <SpiritualLogo size={48} />
                  <div>
                    <h2 className="text-xl font-bold">GANESHA Command Center</h2>
                    <p className="text-white/80 text-sm">Obstacle Remover & Divine Coordinator</p>
                  </div>
                </div>
                <button 
                  onClick={() => setShowGaneshaModal(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
            </div>
            <div className="p-6">
              <textarea
                placeholder="Enter your command... (e.g., 'Create a new task for VISHWAKARMA')"
                className="w-full p-4 border border-gray-200 rounded-lg resize-none text-gray-700"
                style={{ outline: 'none' }}
                onFocus={(e) => e.target.style.borderColor = '#F47216'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                rows={4}
              />
              <div className="flex gap-3 mt-4">
                <button 
                  onClick={() => setShowGaneshaModal(false)}
                  className="flex-1 py-3 border border-gray-200 text-gray-600 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  className="flex-1 py-3 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 hover:opacity-90"
                  style={{ background: '#F47216' }}
                >
                  <Command size={18} />
                  Process Command
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpiritualKailashDashboard;
