import React from 'react';
import AppLayout from '../components/AppLayout';
import { Settings, Wrench, Activity, AlertCircle } from 'lucide-react';

const TattoosTool = () => {
  return (
    <AppLayout showBackButton={true} showMenuButton={true} title="Tattoos Go4Garage Tool">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-purple-500/20 mb-6 shadow-xl">
            <Settings className="w-10 h-10 text-purple-400" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 tracking-tight drop-shadow-lg">
            Tattoos Go4Garage Tool
          </h1>
          <p className="text-lg text-[#8395A7] max-w-2xl mx-auto font-medium leading-relaxed">
            Advanced vehicle diagnostics and service management platform
          </p>
        </div>

        {/* Coming Soon Card */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 backdrop-blur-lg border-2 border-purple-400/30 rounded-2xl p-8 text-center shadow-2xl">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-500/20 mb-6 shadow-lg">
              <AlertCircle className="w-8 h-8 text-yellow-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-4 tracking-tight">Coming Soon</h2>
            <p className="text-base text-[#8395A7] mb-8 font-medium leading-relaxed">
              We're developing a comprehensive vehicle diagnostics platform with real-time monitoring, service scheduling, and maintenance tracking.
            </p>

            {/* Features Preview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <Wrench className="w-8 h-8 text-purple-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">Diagnostics</h3>
                <p className="text-xs text-[#8395A7] font-medium">Real-time vehicle diagnostics</p>
              </div>
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <Activity className="w-8 h-8 text-pink-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">Monitoring</h3>
                <p className="text-xs text-[#8395A7] font-medium">Live performance monitoring</p>
              </div>
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <Settings className="w-8 h-8 text-blue-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">Service Mgmt</h3>
                <p className="text-xs text-[#8395A7] font-medium">Complete service scheduling</p>
              </div>
            </div>

            <div className="mt-8 p-4 bg-[#0A3D62]/20 border border-[#0A3D62]/50 rounded-lg shadow-lg">
              <p className="text-sm text-[#8395A7] font-medium">
                <span className="font-bold text-[#FFC312]">Notify me:</span> Contact{' '}
                <a href="mailto:cto@go4garage.in" className="text-[#FFC312] hover:underline font-semibold">
                  cto@go4garage.in
                </a>{' '}
                to get updates on the launch
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default TattoosTool;
