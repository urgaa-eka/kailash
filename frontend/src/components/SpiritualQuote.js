import React from 'react';
import { getDailyQuote } from '../data/spiritualQuotes';
import '../styles/spiritual-theme.css';

const SpiritualQuote = ({ deityId = null, className = '' }) => {
  const quote = getDailyQuote();
  
  return (
    <div className={`spiritual-quote ${className}`}>
      <p style={{ marginBottom: '8px', fontWeight: '500' }}>{quote.text}</p>
      <p style={{ fontSize: '12px', opacity: '0.8', textAlign: 'right' }}>
        — {quote.source}
      </p>
    </div>
  );
};

export default SpiritualQuote;
