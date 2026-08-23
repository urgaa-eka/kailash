// These sign-in surfaces play an entrance animation on mount; a static capture
// lands mid-fade, so the card shows them at ~15% opacity. The wrapper freezes
// animation on the subtree so the card shows the settled state a user actually
// reads — it changes nothing about the component itself.
import { TwoFactorModal } from 'frontend';

// Rendered open — the modal returns null when isOpen is false.
export const Open = () => (
  <div className="ds-freeze [&_*]:!animate-none">
  <TwoFactorModal isOpen onClose={() => {}} onVerify={() => {}} />
  </div>
);
