import { User } from "lucide-react";
import { Avatar, AvatarFallback } from "./UI/avatar";

export const Header = () => {
  return (
    <header className="h-[8vh] border-b border-[hsl(var(--g4g-gray))] bg-white flex items-center justify-between px-8">
      {/* Left: G4G Logo */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[hsl(var(--g4g-purple))] to-[hsl(var(--g4g-bright-green))] flex items-center justify-center">
          <span className="text-white font-bold text-lg">G4G</span>
        </div>
        <div className="flex flex-col">
          <span className="text-xs font-semibold text-[hsl(var(--g4g-purple))] tracking-wider">GO4GARAGE</span>
        </div>
      </div>
      
      {/* Center: Kailash Title */}
      <div className="flex items-center gap-4">
        <div className="text-center">
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold text-[hsl(var(--g4g-purple))] tracking-[0.15em]">CHARGING POINT</span>
            <div className="h-6 w-px bg-[hsl(var(--g4g-gray))]" />
            <h1 className="text-2xl font-bold">
              <span className="bg-gradient-to-r from-[hsl(var(--g4g-purple))] via-[hsl(var(--g4g-orange))] to-[hsl(var(--g4g-purple))] bg-clip-text text-transparent animate-gradient-slide">Kailash</span>
              {" "}
              <span className="text-[hsl(var(--g4g-purple))]">HUB</span>
            </h1>
          </div>
        </div>
      </div>
      
      {/* Right: Profile */}
      <Avatar className="w-10 h-10 border-2 border-[hsl(var(--g4g-purple))]">
        <AvatarFallback className="bg-[hsl(var(--g4g-purple))] text-white">
          <User className="w-5 h-5" strokeWidth={2} />
        </AvatarFallback>
      </Avatar>
    </header>
  );
};

export default Header;