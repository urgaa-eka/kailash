import { MeditationIndicator } from 'frontend';

// The indicator is a single styled dot from spiritual-theme.css with no content
// of its own, so each cell labels it to give the card something to read.
export const InStatusRow = () => (
  <div className="flex items-center gap-3 rounded-md border px-4 py-3">
    <MeditationIndicator />
    <div>
      <div className="text-sm font-semibold">Kailash is in a meditative state</div>
      <div className="text-xs text-muted-foreground">
        All twenty departments idle, optimal performance
      </div>
    </div>
  </div>
);

export const ActiveAndInactive = () => (
  <div className="space-y-3">
    <div className="flex items-center gap-3">
      <MeditationIndicator active />
      <span className="text-sm">active — the indicator renders</span>
    </div>
    <div className="flex items-center gap-3">
      <span className="inline-block h-4 w-4 rounded-full border border-dashed" />
      <span className="text-sm text-muted-foreground">
        active={'{false}'} — the component returns null, shown here as an empty slot
      </span>
    </div>
  </div>
);
