export const LoginHeader = () => {
  return (
    <header className="h-[8vh] bg-white border-b flex items-center justify-between px-6" style={{ borderColor: 'rgba(87, 6, 131, 0.08)' }}>
      {/* Left: Go4Garage logo */}
      <div className="flex items-center">
        <img 
          src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/4ci0b4px_go4garage-header.png" 
          alt="Go4Garage" 
          className="h-10 w-auto"
        />
      </div>
      
      {/* Right: Kailash Title */}
      <div className="text-right">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-[hsl(var(--g4g-purple))] tracking-[0.15em]">CHARGING POINT</span>
          <div className="h-6 w-px bg-[hsl(var(--g4g-gray))]" />
          <h1 className="text-2xl font-bold">
            <span className="text-[hsl(var(--g4g-purple))]">Kailash</span>
            {" "}
            <span className="text-[hsl(var(--g4g-purple))]">HUB</span>
          </h1>
        </div>
      </div>
    </header>
  );
};

export default LoginHeader;