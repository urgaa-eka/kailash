import { LoginForm } from 'frontend';

// Same faithful defect as LoginBox: LoginForm.js:101 backs its CTA with
// `var(--gradient-primary)`, which is scoped to `.executive-dashboard` and is
// undefined here, so the button paints white-on-nothing. One cell only, since
// `isLoading` only changes that button's label.
// The wrapper also pins opacity and transitions: this form's root carries a
// delayed `animate-slide-up`, and suppressing the animation alone still left the
// capture at ~62% opacity.
export const Default = () => (
  <div className="[&_*]:!animate-none [&_*]:!transition-none [&_*]:!opacity-100 w-[420px]">
    <LoginForm onLogin={() => {}} />
  </div>
);
