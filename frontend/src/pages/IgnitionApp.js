import React from 'react';
import AppLayout from '../components/AppLayout';
import { Zap, MapPin, Gauge, AlertCircle } from 'lucide-react';

const IgnitionApp = () => {
  return (
    <AppLayout showBackButton={true} showMenuButton={true} title="Ignition App">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-orange-500/20 mb-6 shadow-xl">
            <Zap className="w-10 h-10 text-orange-400" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 tracking-tight drop-shadow-lg">
            Ignition App
          </h1>
          <p className="text-lg text-[#8395A7] max-w-2xl mx-auto font-medium leading-relaxed">
            Advanced fleet management and vehicle tracking solution
          </p>
        </div>

        {/* Coming Soon Card */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 backdrop-blur-lg border-2 border-orange-400/30 rounded-2xl p-8 text-center shadow-2xl">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-500/20 mb-6 shadow-lg">
              <AlertCircle className="w-8 h-8 text-yellow-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-4 tracking-tight">Coming Soon</h2>
            <p className="text-base text-[#8395A7] mb-8 font-medium leading-relaxed">
              We're building a powerful fleet management system with real-time GPS tracking, route optimization, and driver behavior analytics.
            </p>

            {/* Features Preview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <MapPin className="w-8 h-8 text-orange-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">GPS Tracking</h3>
                <p className="text-xs text-[#8395A7] font-medium">Real-time fleet location tracking</p>
              </div>
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <Gauge className="w-8 h-8 text-red-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">Performance</h3>
                <p className="text-xs text-[#8395A7] font-medium">Driver behavior analytics</p>
              </div>
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <Zap className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">Optimization</h3>
                <p className="text-xs text-[#8395A7] font-medium">Smart route planning</p>
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

export default IgnitionApp;
