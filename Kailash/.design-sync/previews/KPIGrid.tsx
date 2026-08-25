import {
  KPIGrid,
  SquareKPICard,
  CompactStatCard,
  Zap,
  IndianRupee,
  Users,
  Activity,
} from 'frontend';
// KPIGrid is the layout container the KPI cards are dropped into; it needs real
// children to show anything, and `columns` is its variant axis.
export const FourColumns = () => (
  <div className="w-[720px]">
    <KPIGrid columns={4}>
      <SquareKPICard label="Sessions" value="312" change="8%" icon={Activity} color="purple" />
      <SquareKPICard label="Energy" value="6.8 MWh" change="12%" icon={Zap} color="green" />
      <SquareKPICard label="Revenue" value="₹ 1.1L" change="4%" icon={IndianRupee} color="orange" />
      <SquareKPICard label="Drivers" value="248" change="2%" isPositive={false} icon={Users} color="blue" />
    </KPIGrid>
  </div>
);

export const TwoColumns = () => (
  <div className="w-[460px]">
    <KPIGrid columns={2}>
      <CompactStatCard label="Open faults" value="3" icon={Activity} color="orange" />
      <CompactStatCard label="Stations online" value="41 / 42" icon={Zap} color="green" />
    </KPIGrid>
  </div>
);
