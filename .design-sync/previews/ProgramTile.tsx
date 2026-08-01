import { ProgramTile, Zap, ShieldCheck, Truck } from 'frontend';
export const Default = () => (
  <div className="w-[420px]">
    <ProgramTile
      icon={Zap}
      name="Urjaa Fast Charging"
      badge="Live"
      description="DC fast charging across 42 sites in the NCR corridor"
    />
  </div>
);

export const Stack = () => (
  <div className="w-[420px] space-y-3">
    <ProgramTile
      icon={Zap}
      name="Urjaa Fast Charging"
      badge="Live"
      description="DC fast charging across 42 sites in the NCR corridor"
    />
    <ProgramTile
      icon={Truck}
      name="Fleet Depot"
      badge="Pilot"
      description="Overnight depot charging for last-mile delivery fleets"
    />
    <ProgramTile
      icon={ShieldCheck}
      name="Assured Uptime"
      badge="Beta"
      description="SLA-backed availability with on-site engineer dispatch"
    />
  </div>
);
