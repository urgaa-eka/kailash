import { Calendar } from 'frontend';

// A fixed month keeps the rendered card deterministic across rebuilds — a
// today-relative default would change the sync hash on every calendar day.
const MONTH = new Date(2026, 7, 1);

export const Single = () => (
  <Calendar
    mode="single"
    defaultMonth={MONTH}
    selected={new Date(2026, 7, 14)}
    className="rounded-md border"
  />
);

export const Range = () => (
  <Calendar
    mode="range"
    defaultMonth={MONTH}
    selected={{ from: new Date(2026, 7, 11), to: new Date(2026, 7, 18) }}
    className="rounded-md border"
  />
);

export const WithDisabledDays = () => (
  <Calendar
    mode="single"
    defaultMonth={MONTH}
    selected={new Date(2026, 7, 6)}
    disabled={[{ dayOfWeek: [0, 6] }]}
    className="rounded-md border"
  />
);
