import { DataSourceBadge } from 'frontend';

// The badge palette is tuned for the dark investor dashboard (amber-400 on
// amber-500/20 and friends), so each cell sits on the dark surface it ships
// against rather than on white, where those tints are unreadable.
const Panel = ({ children }) => (
  <div className="rounded-lg bg-[#1a1a2e] p-5">{children}</div>
);

export const Sources = () => (
  <Panel>
    <div className="flex flex-wrap items-center gap-3">
      <DataSourceBadge source="URGAA" />
      <DataSourceBadge source="GSTSAAS" />
      <DataSourceBadge source="IGNITION" />
      <DataSourceBadge source="INTERNAL" />
      <DataSourceBadge source="ALL" />
    </div>
  </Panel>
);

export const WithProvenance = () => (
  <Panel>
    <div className="space-y-3">
      <DataSourceBadge source="URGAA" type="internal" timestamp="2 min ago" />
      <div />
      <DataSourceBadge source="GSTSAAS" type="external" timestamp="14 min ago" />
    </div>
  </Panel>
);

export const TypesOnly = () => (
  <Panel>
    <div className="flex items-center gap-3">
      <DataSourceBadge source="INTERNAL" type="internal" />
      <DataSourceBadge source="IGNITION" type="external" />
    </div>
  </Panel>
);
