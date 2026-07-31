import { FeatureKPICard, Zap, IndianRupee, Gauge } from 'frontend';
export const Colors = () => (
  <div className="grid w-[720px] grid-cols-3 gap-4">
    <FeatureKPICard
      label="Energy dispatched"
      value="48,210 kWh"
      subtitle="Last 7 days, all zones"
      icon={Zap}
      color="green"
    />
    <FeatureKPICard
      label="Settlement"
      value="₹ 4,18,900"
      subtitle="7 OCPI peers"
      icon={IndianRupee}
      color="purple"
    />
    <FeatureKPICard
      label="Peak grid load"
      value="78%"
      subtitle="19:40 IST, no derating"
      icon={Gauge}
      color="orange"
    />
  </div>
);

export const Single = () => (
  <div className="w-[300px]">
    <FeatureKPICard
      label="Uptime"
      value="99.1%"
      subtitle="Rolling 30 days"
      icon={Gauge}
      color="blue"
    />
  </div>
);
