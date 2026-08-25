import { ScrollArea, Separator } from 'frontend';

const FAULTS = [
  'E-19 · Sohna Road · connector 3',
  'E-04 · Cyber City P2 · connector 1',
  'W-22 · Urjaa North Hub · connector 7',
  'E-11 · Manesar · connector 2',
  'W-08 · Gurugram Sector 44 · connector 5',
  'E-19 · Sohna Road · connector 3',
  'W-31 · Cyber City P2 · connector 4',
  'E-02 · Urjaa North Hub · connector 1',
];

export const VerticalList = () => (
  <ScrollArea className="h-56 w-[420px] rounded-md border">
    <div className="p-4">
      <h4 className="mb-3 text-sm font-semibold leading-none">Fault log</h4>
      {FAULTS.map((f, i) => (
        <div key={i}>
          <div className="py-2 font-mono text-xs">{f}</div>
          {i < FAULTS.length - 1 ? <Separator /> : null}
        </div>
      ))}
    </div>
  </ScrollArea>
);

export const Prose = () => (
  <ScrollArea className="h-48 w-[420px] rounded-md border p-4">
    <p className="text-sm leading-relaxed">
      Kailash coordinates twenty departments across the Go4Garage charging network. Grid
      Operations owns load balancing and derating. Customer Care owns disputes, refunds and
      RFID re-issues. Field Maintenance owns preventive schedules and on-site dispatch,
      driven by the anomaly service's connector wear model. Settlement reconciles OCPI peers
      on a weekly window, and the forecasting service projects the next day's demand per
      zone from the prior fourteen days of session data.
    </p>
  </ScrollArea>
);
