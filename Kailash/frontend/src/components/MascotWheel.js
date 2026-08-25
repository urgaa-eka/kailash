import { Zap, Wrench, BarChart3, Truck, Package, Lightbulb, Factory, TrendingUp } from "lucide-react";

export const MascotWheel = () => {
  // Service icons configuration
  const services = [
    { icon: Zap, label: "EV Charging", color: "hsl(var(--g4g-bright-green))" },
    { icon: Wrench, label: "Workshop Services", color: "hsl(var(--g4g-green))" },
    { icon: BarChart3, label: "CPO Dashboard", color: "hsl(var(--g4g-purple))" },
    { icon: Truck, label: "Fleet Management", color: "hsl(var(--g4g-purple-light))" },
    { icon: Package, label: "Parts Supply", color: "hsl(var(--g4g-orange))" },
    { icon: Lightbulb, label: "Energy Management", color: "hsl(var(--g4g-bright-green))" },
    { icon: Factory, label: "Smart Garage", color: "hsl(var(--g4g-green))" },
    { icon: TrendingUp, label: "Business Intelligence", color: "hsl(var(--g4g-purple))" }
  ];

  // Calculate positions on a circle
  const radius = 150; // 300px diameter = 150px radius
  const angleStep = (2 * Math.PI) / services.length;

  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      {/* Rotating wheel container */}
      <div className="relative w-[400px] h-[400px]">
        {/* Service icons wheel */}
        <div className="absolute inset-0 animate-rotate">
          {services.map((service, index) => {
            const angle = index * angleStep - Math.PI / 2; // Start from top
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            
            const Icon = service.icon;
            
            return (
              <div
                key={service.label}
                className="absolute service-icon transition-all duration-300 cursor-pointer pointer-events-auto"
                style={{
                  left: '50%',
                  top: '50%',
                  transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`,
                }}
              >
                <div 
                  className="w-12 h-12 rounded-full flex items-center justify-center border-2 shadow-lg"
                  style={{
                    backgroundColor: `${service.color.replace(')', ' / 0.15)')}`,
                    borderColor: service.color
                  }}
                >
                  <Icon 
                    className="w-6 h-6" 
                    strokeWidth={1.5}
                    style={{ color: service.color }}
                  />
                </div>
                <div className="text-xs text-center mt-1 font-medium" style={{ color: service.color }}>
                  {service.label}
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Mascot in center */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-mascot-bounce pointer-events-auto">
            <img 
              src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png" 
              alt="Go4Garage Mascot" 
              className="w-48 h-48 object-contain"
              style={{ filter: 'drop-shadow(0 10px 20px rgba(87, 6, 131, 0.2))' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MascotWheel;