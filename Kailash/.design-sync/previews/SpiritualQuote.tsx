import { SpiritualQuote } from 'frontend';

// `deityId` is accepted but never used: SpiritualQuote.js destructures it and
// then calls getDailyQuote() with no argument, so every instance renders the same
// daily quote. There is deliberately no per-deity story here, because the axis
// does not exist — showing two identical cards would advertise a variant the
// component cannot produce.
export const Default = () => (
  <div className="w-[460px]">
    <SpiritualQuote />
  </div>
);
