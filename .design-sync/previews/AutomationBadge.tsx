import { AutomationBadge } from 'frontend';

const Panel = ({ children }) => (
  <div className="rounded-lg bg-[#1a1a2e] p-5">{children}</div>
);

export const AutomatedAndManual = () => (
  <Panel>
    <div className="flex items-center gap-4">
      <AutomationBadge automated />
      <AutomationBadge automated={false} />
    </div>
  </Panel>
);

export const WithoutLabel = () => (
  <Panel>
    <div className="flex items-center gap-4">
      <AutomationBadge automated showLabel={false} />
      <AutomationBadge automated={false} showLabel={false} />
    </div>
  </Panel>
);
