// These sign-in surfaces play an entrance animation on mount; a static capture
// lands mid-fade, so the card shows them at ~15% opacity. The wrapper freezes
// animation on the subtree so the card shows the settled state a user actually
// reads — it changes nothing about the component itself.
import { LoginCardOverlay } from 'frontend';

// The overlay variant of the sign-in card — positioned over the landing page's
// animated background, hence the single-story card override.
export const Default = () => (
  <div className="ds-freeze [&_*]:!animate-none"><LoginCardOverlay onLogin={() => {}} /></div>
);

export const Submitting = () => (
  <div className="ds-freeze [&_*]:!animate-none"><LoginCardOverlay onLogin={() => {}} isLoading /></div>
);
