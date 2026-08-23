import React from 'react';
import { getDeityImage } from '../data/deityImages';
import '../styles/spiritual-theme.css';

const DeityAvatar = ({ deityId, size = 48, className = '', showGlow = false }) => {
  const deity = getDeityImage(deityId);
  
  const sizeStyle = {
    width: `${size}px`,
    height: `${size}px`,
    minWidth: `${size}px`,
    minHeight: `${size}px`
  };
  
  return (
    <div 
      className={`deity-avatar-wrapper ${showGlow ? 'divine-glow' : ''} ${className}`}
      style={sizeStyle}
      title={deity.alt}
    >
      <img 
        src={deity.primary} 
        alt={deity.alt}
        className="deity-avatar-img"
        onError={(e) => {
          // Fallback to default if image fails to load
          e.target.src = getDeityImage('default').primary;
        }}
      />
    </div>
  );
};

export default DeityAvatar;
