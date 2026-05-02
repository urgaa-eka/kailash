import React from 'react';
import '../styles/spiritual-theme.css';

const MeditationIndicator = ({ active = true, className = '' }) => {
  if (!active) return null;
  
  return (
    <div 
      className={`meditation-indicator ${className}`}
      title="System in meditative state - optimal performance"
      aria-label="Meditation indicator"
    />
  );
};

export default MeditationIndicator;
