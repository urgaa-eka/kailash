import { Zap, BatteryCharging, Wrench, Car, Building2, Award, Users, Package } from "lucide-react";
import ProductCard from "./ProductCard";
import ProgramTile from "./ProgramTile";
import ServiceRow from "./ServiceRow";
import MadeInBharatBadge from "./MadeInBharatBadge";

export const LeftPanel = () => {
  const products = [
    {
      icon: Zap,
      name: "IGNITION",
      description: "Efficiency, Trust & Growth Platform",
      gradient: "from-[hsl(var(--g4g-purple))] via-[hsl(var(--g4g-green))] to-[hsl(var(--g4g-orange))]"
    },
    {
      icon: BatteryCharging,
      name: "URGAA",
      description: "India's First EV Infrastructure Ecosystem"
    },
    {
      icon: Wrench,
      name: "Go4Garage Service Tools",
      description: "Advanced Diagnostics & Management Suite"
    }
  ];

  const programs = [
    {
      icon: Car,
      name: "MG Model Programme",
      badge: "Premium",
      description: "Partner with leading automotive manufacturers"
    },
    {
      icon: Building2,
      name: "OEM Support",
      badge: "Certified",
      description: "Direct collaboration with OEMs"
    },
    {
      icon: Award,
      name: "Mandate WorkShop",
      badge: "Training",
      description: "Certified training & compliance programs"
    }
  ];

  const services = [
    {
      icon: Users,
      name: "B2B Services",
      description: "Enterprise fleet & charging management"
    },
    {
      icon: Package,
      name: "Spare & Parts Distribution",
      description: "Authentic components, pan-India delivery"
    },
    {
      icon: BatteryCharging,
      name: "EV Charging Infrastructure",
      description: "Complete charging operations & monitoring"
    }
  ];

  return (
    <aside className="w-[38%] h-[92vh] overflow-hidden bg-gradient-to-b from-[#FAFAFA] to-[#F5F3F7] border-r border-[hsl(var(--g4g-gray))]">
      <div className="p-6 space-y-5">
        {/* Products Section */}
        <section>
          <h2 className="text-sm font-bold text-[hsl(var(--g4g-purple))] mb-3 relative inline-block">
            Our Products
            <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-gradient-to-r from-[hsl(var(--g4g-purple))] to-[hsl(var(--g4g-bright-green))]" />
          </h2>
          <div className="space-y-2">
            {products.map((product) => (
              <ProductCard key={product.name} {...product} />
            ))}
          </div>
        </section>

        {/* Partner Programs Section */}
        <section>
          <h2 className="text-sm font-bold text-[hsl(var(--g4g-purple))] mb-3">Partner Programs</h2>
          <div className="space-y-2">
            {programs.map((program) => (
              <ProgramTile key={program.name} {...program} />
            ))}
          </div>
        </section>

        {/* Services Section */}
        <section>
          <h2 className="text-sm font-bold text-[hsl(var(--g4g-purple))] mb-3">Service Excellence</h2>
          <div className="space-y-0">
            {services.map((service) => (
              <ServiceRow key={service.name} {...service} />
            ))}
          </div>
        </section>

        {/* Made In Bharat Badge */}
        <MadeInBharatBadge />
      </div>
    </aside>
  );
};

export default LeftPanel;