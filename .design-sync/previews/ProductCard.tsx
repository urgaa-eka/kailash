import {
  ProductCard,
  Zap,
  Truck,
  ShieldCheck,
  Battery,
} from 'frontend';
// `gradient` is a Tailwind gradient class pair applied to the icon chip and the
// left border, e.g. "from-purple-600 to-green-600".
export const Default = () => (
  <div className="w-[380px]">
    <ProductCard
      icon={Zap}
      name="Urjaa Fast Charging"
      description="DC fast charging across 42 sites in the NCR corridor"
      gradient="from-purple-700 to-green-600"
    />
  </div>
);

export const Gradients = () => (
  <div className="w-[380px] space-y-3">
    <ProductCard
      icon={Zap}
      name="Urjaa Fast Charging"
      description="DC fast charging across the NCR corridor"
      gradient="from-purple-700 to-green-600"
    />
    <ProductCard
      icon={Truck}
      name="Fleet Depot"
      description="Overnight depot charging for delivery fleets"
      gradient="from-orange-500 to-amber-400"
    />
    <ProductCard
      icon={Battery}
      name="Battery Health"
      description="State-of-health telemetry per connector"
      gradient="from-emerald-600 to-teal-400"
    />
  </div>
);

export const WithoutGradient = () => (
  <div className="w-[380px]">
    <ProductCard
      icon={ShieldCheck}
      name="Assured Uptime"
      description="Falls back to the brand purple chip when no gradient is given"
    />
  </div>
);
