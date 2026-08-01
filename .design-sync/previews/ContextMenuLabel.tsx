import * as React from 'react';
import {
  ContextMenu,
  ContextMenuTrigger,
  ContextMenuContent,
  ContextMenuLabel,
  ContextMenuItem,
  ContextMenuSeparator,
} from 'frontend';

// ContextMenuLabel is a heading inside the menu surface — it has no box of its
// own, and the surface only mounts on a real contextmenu event (see the note in
// ContextMenu.tsx), so the cell dispatches that event.
function useRightClick() {
  const ref = React.useRef(null);
  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    el.dispatchEvent(
      new MouseEvent('contextmenu', {
        bubbles: true,
        cancelable: true,
        view: window,
        clientX: r.left + 40,
        clientY: r.top + 24,
      }),
    );
  }, []);
  return ref;
}

export const SectionHeadings = () => {
  const ref = useRightClick();
  return (
    <ContextMenu>
      <ContextMenuTrigger
        ref={ref}
        className="flex h-24 w-[260px] items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground"
      >
        Session row (right-click)
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        <ContextMenuLabel>Session</ContextMenuLabel>
        <ContextMenuItem>Stop</ContextMenuItem>
        <ContextMenuItem>Refund</ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuLabel>Connector</ContextMenuLabel>
        <ContextMenuItem>Reset</ContextMenuItem>
        <ContextMenuItem>Lock out</ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
};
