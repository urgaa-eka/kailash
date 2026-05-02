import React from 'react';
import { Briefcase } from 'lucide-react';
import '../styles/spiritual-theme.css';

const DepartmentTag = ({ departmentName, position, className = '' }) => {
  return (
    <div className={`department-tag ${className}`}>
      <Briefcase size={14} />
      <span>
        {departmentName}
        {position && <span className="position-badge">{position}</span>}
      </span>
    </div>
  );
};

export default DepartmentTag;
