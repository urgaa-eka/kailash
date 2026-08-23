export const LoadingState = () => {
  return (
    <div className="h-screen w-screen flex items-center justify-center bg-white">
      <div className="text-center">
        <div className="relative inline-block mb-6">
          <img 
            src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png" 
            alt="Go4Garage Mascot" 
            className="w-32 h-32 object-contain animate-bounce"
            style={{ filter: 'drop-shadow(0 10px 20px rgba(87, 6, 131, 0.2))' }}
          />
        </div>
        
        <div className="text-base font-semibold text-[hsl(var(--g4g-purple))] mb-4">
          Initializing Kailash...
        </div>
        
        <div className="flex gap-2 justify-center">
          <span 
            className="w-2 h-2 bg-[hsl(var(--g4g-bright-green))] rounded-full animate-pulse" 
            style={{ animationDelay: '0ms' }}
          />
          <span 
            className="w-2 h-2 bg-[hsl(var(--g4g-bright-green))] rounded-full animate-pulse" 
            style={{ animationDelay: '150ms' }}
          />
          <span 
            className="w-2 h-2 bg-[hsl(var(--g4g-bright-green))] rounded-full animate-pulse" 
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  );
};

export default LoadingState;