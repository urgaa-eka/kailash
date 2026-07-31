import { Sidebar } from 'frontend';

// The sidebar is a fixed panel that the app mounts inside `.app-layout` (see
// MainLayout); standalone it loses that container and paints without its
// surface. The stage below is the same wrapper the app gives it.
export const Open = () => (
  <div className="app-layout relative h-[620px] w-[280px] overflow-hidden">
    <Sidebar isOpen onClose={() => {}} />
  </div>
);
