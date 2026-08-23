import { ExternalLink } from "lucide-react";

export const MinimalHeader = () => {
  return (
    <header 
      className="h-[8vh] flex items-center justify-between px-6" 
      style={{ 
        backgroundColor: '#ffffff'
      }}
    >
      {/* Left: Go4Garage logo */}
      <div className="flex items-center gap-3">
        <img 
          src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/4ci0b4px_go4garage-header.png" 
          alt="Go4Garage" 
          className="h-10 w-auto"
        />
      </div>

      {/* Right: Kailash AI branding */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-semibold text-[#8172AD]">KAILASH AI</span>
      </div>
    </header>
  );
};

export default MinimalHeader;