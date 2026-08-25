import React from 'react';
import { useGuardianStatus } from '../hooks/useApi';
import { Shield, Activity, Brain, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';

const guardianIcons = {
  SHIV: Shield,
  PARVATI: Activity,
  GANESHA: Brain
};

const guardianColors = {
  SHIV: 'text-red-500 bg-red-100',
  PARVATI: 'text-green-500 bg-green-100',
  GANESHA: 'text-g4g-blue bg-blue-100'
};

const Guardians = () => {
  const { data, isLoading, error } = useGuardianStatus();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error loading guardians: {error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="border-b pb-4">
        <h1 className="text-3xl font-bold" style={{ color: '#0A3D62' }}>Guardian System</h1>
        <p className="text-gray-600 mt-2">Monitor and manage the three primary guardians of Kailash</p>
      </div>
      
      <div className="grid md:grid-cols-3 gap-6">
        {data?.guardians?.map((guardian) => {
          const Icon = guardianIcons[guardian.guardian] || Shield;
          const colorClass = guardianColors[guardian.guardian] || 'text-gray-500 bg-gray-100';
          
          return (
            <div 
              key={guardian.guardian} 
              className="bg-white rounded-xl border-2 p-6 hover:shadow-lg transition-shadow"
              style={{ borderColor: guardian.status === 'active' ? '#0A3D62' : '#FFC312' }}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-3 rounded-lg ${colorClass}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg" style={{ color: '#0A3D62' }}>
                    {guardian.guardian}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {guardian.status === 'active' ? 'Operational' : 'Warning'}
                  </p>
                </div>
                {guardian.status === 'active' ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertTriangle className="w-5 h-5" style={{ color: '#FFC312' }} />
                )}
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="font-medium" style={{ color: guardian.status === 'active' ? '#4CAF50' : '#FFC312' }}>
                    {guardian.status.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Heartbeat:</span>
                  <span className="font-medium text-gray-800">
                    {new Date(guardian.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <p className="text-xs text-gray-400">
                  Monitoring and orchestrating KAILASH operations
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-xl font-semibold mb-4" style={{ color: '#0A3D62' }}>Guardian Roles</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <h3 className="font-medium text-red-600 mb-2">SHIV (Security)</h3>
            <p className="text-sm text-gray-600">Protection, threat detection, access control, and security monitoring</p>
          </div>
          <div>
            <h3 className="font-medium text-green-600 mb-2">PARVATI (Workflow)</h3>
            <p className="text-sm text-gray-600">Task distribution, department coordination, and workflow optimization</p>
          </div>
          <div>
            <h3 className="font-medium text-g4g-blue mb-2">GANESHA (Orchestration)</h3>
            <p className="text-sm text-gray-600">AI-powered orchestration, intent classification, and intelligent routing</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Guardians;