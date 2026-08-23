import React from 'react';
import { Search, Bell } from 'lucide-react';
import EnhancedUserProfile from './EnhancedUserProfile';
import MeditationIndicator from './MeditationIndicator';
import '../styles/spiritual-theme.css';

const SpiritualDashboardHeader = ({ onGaneshaClick }) => {
  return (
    <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 px-8 py-5 fixed top-0 left-0 right-0 z-50 shadow-sm">
      <div className="flex items-center justify-between max-w-[2000px] mx-auto">
        {/* Logo Section with Om Symbol */}
        <div className="flex items-center gap-6">
          <div className="relative">
            <div className="absolute -inset-1 bg-gradient-divine rounded-lg blur opacity-25" />
            <div className="relative flex items-center gap-3">
              <span className="om-symbol text-2xl"></span>
              <div>
                <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-sacred tracking-tight leading-none">
                  KAILASH
                </h1>
                <p className="text-xs text-gray-500 font-medium tracking-wide uppercase mt-0.5 flex items-center gap-2">
                  Command Center
                  <MeditationIndicator active={true} />
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-xl mx-12">
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-sacred rounded-xl blur opacity-0 group-hover:opacity-20 transition duration-300" />
            <div className="relative">
              <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 transition-colors group-hover:text-sacred-saffron">
                <Search size={20} />
              </div>
              <input
                type="text"
                placeholder="Search departments, tasks, analytics..."
                className="w-full pl-12 pr-6 py-3.5 bg-white border border-gray-200 rounded-xl text-base font-normal text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-sacred-gold/50 focus:border-sacred-gold transition-all duration-300 shadow-sm hover:shadow-md"
              />
            </div>
          </div>
        </div>

        {/* Actions Section */}
        <div className="flex items-center gap-4">
          {/* GANESHA Button with Divine Glow */}
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-red-600 to-red-700 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition duration-300" />
            <button
              onClick={onGaneshaClick}
              className="relative px-8 py-3.5 bg-gradient-to-r from-red-600 to-red-700 text-white text-base font-bold rounded-xl hover:from-red-700 hover:to-red-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95 flex items-center gap-2"
            >
              <span></span>
              GANESHA
            </button>
          </div>

          {/* Notifications */}
          <button className="relative p-3 text-gray-600 hover:text-sacred-saffron transition-all duration-300 hover:bg-sacred-gold-light rounded-xl group">
            <Bell size={20} />
            <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-600 rounded-full animate-pulse ring-4 ring-white" />
          </button>

          {/* User Profile */}
          <EnhancedUserProfile 
            name="Vivek Gupta"
            role="Chief Executive Officer"
            department="KAILASH"
            deityId="ganesha"
            showMeditation={true}
          />
        </div>
      </div>
    </header>
  );
};

export default SpiritualDashboardHeader;
