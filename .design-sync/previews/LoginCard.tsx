// These sign-in surfaces play an entrance animation on mount; a static capture
// lands mid-fade, so the card shows them at ~15% opacity. The wrapper freezes
// animation on the subtree so the card shows the settled state a user actually
// reads — it changes nothing about the component itself.
import { LoginCard } from 'frontend';

export const Default = () => (
  <div className="ds-freeze [&_*]:!animate-none">
  <div className="w-[460px]">
      <LoginCard onLogin={() => {}} />
    </div>
  </div>
);

export const Submitting = () => (
  <div className="ds-freeze [&_*]:!animate-none">
  <div className="w-[460px]">
      <LoginCard onLogin={() => {}} isLoading />
    </div>
  </div>
);
