export const MadeInBharatBadge = () => {
  return (
    <div className="relative rounded-2xl p-5 text-center overflow-hidden" style={{ background: 'linear-gradient(135deg, #570683 0%, #DF8C4D 50%, #0DA34E 100%)', boxShadow: '0 4px 16px rgba(87, 6, 131, 0.2)' }}>
      <div className="flex items-center justify-center gap-2 mb-1">
        <span className="text-2xl">🇮🇳</span>
        <h3 className="text-lg font-bold text-white tracking-wider">MADE IN BHARAT</h3>
      </div>
      <p className="text-sm text-white/90 font-medium">Powering India's EV Revolution</p>
      
      {/* Elephant Mascot */}
      <div className="absolute bottom-2 left-2 w-14 h-14" style={{ transform: 'rotate(15deg)' }}>
        <img 
          src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png" 
          alt="Mascot" 
          className="w-full h-full object-contain"
          style={{ filter: 'drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2))' }}
        />
      </div>
    </div>
  );
};

export default MadeInBharatBadge;