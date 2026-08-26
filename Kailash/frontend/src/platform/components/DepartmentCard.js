import React from 'react';
import { Briefcase, Users, CheckCircle2 } from 'lucide-react';
import DeityAvatar from './DeityAvatar';
import '../styles/spiritual-theme.css';

const DepartmentCard = ({ department, onClick, isActive = false }) => {
  const { id, name, chief, role, activeTasks, workload, status } = department;
  
  return (
    <button
      onClick={onClick}
      className={`w-full group relative ${isActive ? 'ring-2 ring-sacred-gold' : ''}`}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-purple-600 rounded-xl opacity-0 group-hover:opacity-10 transition-all duration-300" />
      <div className="relative flex items-center gap-3 px-4 py-3.5 text-gray-700 hover:text-gray-900 rounded-xl transition-all duration-300 group-hover:bg-white group-hover:shadow-md border-l-4 border-transparent group-hover:border-sacred-gold">
        <DeityAvatar deityId={id} size={40} showGlow={false} />
        
        <div className="flex-1 text-left">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold block">{name}</span>
            <span className="blessing-badge">{chief}</span>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs font-normal text-gray-500">{role}</span>
          </div>
          <div className="flex items-center gap-3 mt-2">
            <span className="flex items-center gap-1 text-xs text-gray-600">
              <Briefcase size={12} />
              {activeTasks} tasks
            </span>
            <span className="flex items-center gap-1 text-xs text-gray-600">
              <Users size={12} />
              {workload}% load
            </span>
          </div>
        </div>
        
        <div className={`w-2 h-2 rounded-full ring-4 ${
          status === 'active' ? 'bg-green-500 ring-green-100' : 'bg-gray-300 ring-gray-100'
        }`} />
      </div>
    </button>
  );
};

export default DepartmentCard;
