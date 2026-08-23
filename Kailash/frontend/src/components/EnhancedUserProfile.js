import React from 'react';
import { User } from 'lucide-react';
import DeityAvatar from './DeityAvatar';
import MeditationIndicator from './MeditationIndicator';
import '../styles/spiritual-theme.css';

const EnhancedUserProfile = ({ 
  name = 'Vivek Gupta', 
  role = 'Chief Executive Officer',
  department = 'KAILASH',
  deityId = 'ganesha',
  showMeditation = true
}) => {
  return (
    <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
      <DeityAvatar deityId={deityId} size={40} />
      <div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-900">{name}</span>
          {showMeditation && <MeditationIndicator />}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-normal text-gray-500">{role}</span>
          <span className="position-badge">{department}</span>
        </div>
      </div>
    </div>
  );
};

export default EnhancedUserProfile;
