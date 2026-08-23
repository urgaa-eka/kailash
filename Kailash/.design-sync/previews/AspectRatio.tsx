import { AspectRatio } from 'frontend';

// AspectRatio ships no visuals of its own — it only constrains its child's box.
// These cells give it a visible child so the constraint is legible.
export const Ratio16x9 = () => (
  <div className="w-[420px]">
    <AspectRatio ratio={16 / 9}>
      <div className="flex h-full w-full items-center justify-center rounded-md bg-[hsl(var(--g4g-purple))] text-sm font-medium text-white">
        16 / 9 — station hero
      </div>
    </AspectRatio>
  </div>
);

export const Square = () => (
  <div className="w-[260px]">
    <AspectRatio ratio={1}>
      <div className="flex h-full w-full items-center justify-center rounded-md bg-[hsl(var(--g4g-green))] text-sm font-medium text-white">
        1 / 1 — map tile
      </div>
    </AspectRatio>
  </div>
);

export const Ultrawide = () => (
  <div className="w-[420px]">
    <AspectRatio ratio={21 / 9}>
      <div className="flex h-full w-full items-center justify-center rounded-md border bg-muted text-sm text-muted-foreground">
        21 / 9 — dashboard banner
      </div>
    </AspectRatio>
  </div>
);
