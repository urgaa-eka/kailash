import {
  CompactStatCard,
  Zap,
  Activity,
  Users,
  IndianRupee,
} from 'frontend';
export const Row = () => (
  <div className="grid w-[720px] grid-cols-4 gap-4">
    <CompactStatCard label="Stations online" value="41 / 42" icon={Zap} color="green" />
    <CompactStatCard label="Open faults" value="3" icon={Activity} color="orange" />
    <CompactStatCard label="Active drivers" value="248" icon={Users} color="blue" />
    <CompactStatCard label="Billed today" value="₹ 1,84,200" icon={IndianRupee} color="purple" />
  </div>
);

export const Single = () => (
  <div className="w-[240px]">
    <CompactStatCard label="Energy dispatched" value="6.8 MWh" icon={Zap} color="green" />
  </div>
);
