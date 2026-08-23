import { DeityAvatar } from 'frontend';

// deityId keys into src/data/deityImages.js — one avatar per department chief.
export const Departments = () => (
  <div className="flex items-center gap-4">
    <DeityAvatar deityId="ganesha" size={56} />
    <DeityAvatar deityId="vishwakarma" size={56} />
    <DeityAvatar deityId="lakshmi" size={56} />
    <DeityAvatar deityId="kubera" size={56} />
  </div>
);

export const Sizes = () => (
  <div className="flex items-end gap-4">
    <DeityAvatar deityId="ganesha" size={32} />
    <DeityAvatar deityId="ganesha" size={48} />
    <DeityAvatar deityId="ganesha" size={72} />
  </div>
);

export const WithGlow = () => (
  <div className="flex items-center gap-6">
    <DeityAvatar deityId="surya" size={64} showGlow />
    <DeityAvatar deityId="surya" size={64} />
  </div>
);
