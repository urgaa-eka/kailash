import * as React from 'react';
import {
  ContextMenu,
  ContextMenuTrigger,
  ContextMenuContent,
  ContextMenuLabel,
  ContextMenuItem,
  ContextMenuCheckboxItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
} from 'frontend';

// A context menu has no `open` prop — Radix opens it from a real contextmenu
// event, and ContextMenuContent's internal Portal is gated on that state, so
// forceMount cannot substitute. Dispatching the event the component actually
// listens for is the only way to capture the open surface, and it exercises the
// real code path rather than faking the markup.
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

export const Open = () => {
  const ref = useRightClick();
  return (
    <ContextMenu>
      <ContextMenuTrigger
        ref={ref}
        className="flex h-24 w-[260px] items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground"
      >
        Station row (right-click)
      </ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        <ContextMenuLabel>Urjaa North Hub</ContextMenuLabel>
        <ContextMenuSeparator />
        <ContextMenuItem>
          Open session log
          <ContextMenuShortcut>⌘L</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuItem>Copy station id</ContextMenuItem>
        <ContextMenuCheckboxItem checked>Pin to dashboard</ContextMenuCheckboxItem>
        <ContextMenuSeparator />
        <ContextMenuItem className="text-destructive">Decommission</ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
};
