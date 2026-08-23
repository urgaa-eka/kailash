import { MadeInBharatBadge } from 'frontend';

// Takes no props — the badge is a fixed brand mark.
export const Default = () => <MadeInBharatBadge />;

export const OnDarkSurface = () => (
  <div className="rounded-lg bg-[#1a1a2e] p-6">
    <MadeInBharatBadge />
  </div>
);
