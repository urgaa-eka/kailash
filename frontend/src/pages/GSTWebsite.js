import React from 'react';
import AppLayout from '../components/AppLayout';
import { FileText, Calendar, DollarSign, AlertCircle } from 'lucide-react';

const GSTWebsite = () => {
  return (
    <AppLayout showBackButton={true} showMenuButton={true} title="GST Website">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/20 mb-6 shadow-xl">
            <FileText className="w-10 h-10 text-green-400" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4 tracking-tight drop-shadow-lg">
            GST Compliance & Filing
          </h1>
          <p className="text-lg text-[#8395A7] max-w-2xl mx-auto font-medium leading-relaxed">
            Complete GST management system for Go4Garage operations
          </p>
        </div>

        {/* Coming Soon Card */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 backdrop-blur-lg border-2 border-green-400/30 rounded-2xl p-8 text-center shadow-2xl">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-500/20 mb-6 shadow-lg">
              <AlertCircle className="w-8 h-8 text-yellow-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-4 tracking-tight">Coming Soon</h2>
            <p className="text-base text-[#8395A7] mb-8 font-medium leading-relaxed">
              We're building a comprehensive GST compliance platform with automated filing, invoice management, and real-time compliance tracking.
            </p>

            {/* Features Preview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <FileText className="w-8 h-8 text-green-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">Invoice Management</h3>
                <p className="text-xs text-[#8395A7] font-medium">Digital invoicing with GST compliance</p>
              </div>
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <Calendar className="w-8 h-8 text-blue-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">Auto Filing</h3>
                <p className="text-xs text-[#8395A7] font-medium">Automated GST return filing</p>
              </div>
              <div className="bg-[#222F3E]/50 rounded-xl p-4 border border-white/10 shadow-lg">
                <DollarSign className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
                <h3 className="text-sm font-bold text-white mb-2">Tax Reports</h3>
                <p className="text-xs text-[#8395A7] font-medium">Detailed tax analytics & reports</p>
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

export default GSTWebsite;
