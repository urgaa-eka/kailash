import { NeuralNetworkMap } from "./NeuralNetworkMap";
import LoginCard from "./LoginCard";
import FloatingOrbs from "./FloatingOrbs";

export const RightPanel = ({ onLogin, isLoading }) => {
  return (
    <div className="w-[62%] h-[92vh] relative overflow-hidden tech-grid animate-grid-pulse">
      {/* Floating gradient orbs */}
      <FloatingOrbs />
      
      {/* Dual-ring wheel showcase */}
      <NeuralNetworkMap />
      
      {/* Login card overlay */}
      <LoginCard onLogin={onLogin} isLoading={isLoading} />
    </div>
  );
};

export default RightPanel;