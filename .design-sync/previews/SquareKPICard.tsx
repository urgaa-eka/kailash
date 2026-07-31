import {
  SquareKPICard,
  Zap,
  IndianRupee,
  Users,
  Activity,
} from 'frontend';
export const Colors = () => (
  <div className="grid w-[720px] grid-cols-4 gap-4">
    <SquareKPICard label="Sessions" value="312" change="8%" icon={Activity} color="blue" />
    <SquareKPICard label="Energy" value="6.8 MWh" change="12%" icon={Zap} color="green" />
    <SquareKPICard label="Revenue" value="₹ 1.1L" change="4%" icon={IndianRupee} color="orange" />
    <SquareKPICard label="Drivers" value="248" change="2%" icon={Users} color="purple" />
  </div>
);

export const TrendDirection = () => (
  <div className="grid w-[380px] grid-cols-2 gap-4">
    <SquareKPICard label="Uptime" value="99.1%" change="0.4%" isPositive icon={Activity} color="green" />
    <SquareKPICard label="Faults" value="3" change="50%" isPositive={false} icon={Zap} color="orange" />
  </div>
);
