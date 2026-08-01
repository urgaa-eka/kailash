import { SessionTimeout } from 'frontend';

// SessionTimeout is a watchdog: it renders its warning only once the idle timer
// is close to expiry, so an authenticated mount shows the resting (empty) state
// and the unauthenticated mount is a no-op. Both are real states; neither can be
// fast-forwarded in a static capture.
export const Authenticated = () => (
  <div className="rounded-md border border-dashed px-4 py-6 text-sm text-muted-foreground">
    <SessionTimeout isAuthenticated />
    Mounted with isAuthenticated — the countdown runs silently until the idle
    threshold is reached, then a warning dialog appears.
  </div>
);
