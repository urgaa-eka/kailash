import { ProblemResolutionCard } from 'frontend';

const Panel = ({ children }) => (
  <div className="rounded-lg bg-[#1a1a2e] p-5">{children}</div>
);

export const Automated = () => (
  <Panel>
    <ProblemResolutionCard
      problem="Transformer at Sohna Road crossed 85% of rated capacity during the evening peak"
      solution="Grid Operations stepped output down in 10 kW increments and restored full rate after eleven minutes"
      source="URGAA"
      type="internal"
      automated
      timestamp="18 min ago"
      savings="₹ 12,400"
    />
  </Panel>
);

export const Manual = () => (
  <Panel>
    <ProblemResolutionCard
      problem="Connector CP-03 raised fault E-19 twice within an hour"
      solution="Field Maintenance dispatched an engineer; connector locked out pending inspection"
      source="INTERNAL"
      type="internal"
      automated={false}
      timestamp="2 h ago"
      savings="₹ 3,100"
    />
  </Panel>
);

export const Compact = () => (
  <Panel>
    <ProblemResolutionCard
      problem="Settlement mismatch against ChargeZone for the 14 July window"
      solution="Reconciled from OCPI CDRs and reissued the invoice"
      source="GSTSAAS"
      type="external"
      automated
      timestamp="yesterday"
      savings="₹ 51,640"
      compact
    />
  </Panel>
);
