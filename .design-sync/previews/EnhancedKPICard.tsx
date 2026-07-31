import { EnhancedKPICard, Zap, IndianRupee, AlertTriangle } from 'frontend';
// EnhancedKPICard interpolates {icon} directly, so it takes a rendered element
// rather than a component type — unlike ProgramTile/ProductCard/ServiceRow,
// which destructure it as "icon: Icon" and render <Icon />.

const Panel = ({ children }) => (
  <div className="rounded-lg bg-[#1a1a2e] p-5">{children}</div>
);

export const Default = () => (
  <Panel>
    <EnhancedKPICard
      title="Energy dispatched"
      value="48,210 kWh"
      source="URGAA"
      type="internal"
      timestamp="2 min ago"
      trend="12.4%"
      trendDirection="up"
      description="Last 7 days, all zones"
      icon={<Zap className="h-4 w-4" />}
    />
  </Panel>
);

export const TrendDown = () => (
  <Panel>
    <EnhancedKPICard
      title="Manual interventions"
      value="8"
      source="INTERNAL"
      type="internal"
      timestamp="just now"
      trend="31%"
      trendDirection="down"
      description="Fewer hands-on fixes than last week"
      icon={<AlertTriangle className="h-4 w-4" />}
    />
  </Panel>
);

export const AICalculated = () => (
  <Panel>
    <EnhancedKPICard
      title="Projected settlement"
      value="₹ 4,18,900"
      source="GSTSAAS"
      type="external"
      timestamp="14 min ago"
      trend="4.1%"
      trendDirection="up"
      aiCalculated
      description="Forecast for the closing OCPI window"
      icon={<IndianRupee className="h-4 w-4" />}
    />
  </Panel>
);
