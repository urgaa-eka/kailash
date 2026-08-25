import {
  ServiceRow,
  Zap,
  Wrench,
  IndianRupee,
  Radio,
} from 'frontend';
export const Default = () => (
  <div className="w-[420px]">
    <ServiceRow
      icon={Zap}
      name="Charge Point Operations"
      description="Session lifecycle, tariffs and connector state"
    />
  </div>
);

export const List = () => (
  <div className="w-[420px]">
    <ServiceRow
      icon={Zap}
      name="Charge Point Operations"
      description="Session lifecycle, tariffs and connector state"
    />
    <ServiceRow
      icon={Wrench}
      name="Field Maintenance"
      description="Preventive schedules and on-site engineer dispatch"
    />
    <ServiceRow
      icon={IndianRupee}
      name="Settlement"
      description="Weekly OCPI reconciliation across seven peers"
    />
    <ServiceRow
      icon={Radio}
      name="Roaming"
      description="Partner networks starting sessions on Urjaa hardware"
    />
  </div>
);
