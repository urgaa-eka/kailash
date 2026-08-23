import { LoginBox } from 'frontend';

// The CTA renders with no background. That is faithful, not a preview fault:
// LoginBox.js:116 sets style={{ background: 'var(--gradient-primary)' }}, and
// that variable is declared only under `.executive-dashboard` in
// pages/Executive.css — the sign-in screen has no such ancestor, so it resolves
// to nothing and the inline style beats the Button's own `bg-primary`.
// Only one cell: `isLoading` changes just the CTA label, and with the CTA
// invisible the two states are indistinguishable.
export const Default = () => (
  <div className="[&_*]:!animate-none w-[460px]">
    <LoginBox onLogin={() => {}} />
  </div>
);
