import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from 'frontend';

// react-resizable-panels measures its group's box to lay panels out, and it does
// not get a definite height from a Tailwind class here — the vertical group
// collapsed to a bare handle rule. Inline heights can't be purged or
// out-specified, so both cells set one directly.
export const Horizontal = () => (
  <div className="rounded-lg border" style={{ height: 220, width: 460 }}>
    <ResizablePanelGroup direction="horizontal" style={{ height: '100%' }}>
      <ResizablePanel defaultSize={35} minSize={20}>
        <div className="flex h-full items-center justify-center p-4 text-sm">Zones</div>
      </ResizablePanel>
      <ResizableHandle withHandle />
      <ResizablePanel defaultSize={65} minSize={20}>
        <div className="flex h-full items-center justify-center p-4 text-sm">Station detail</div>
      </ResizablePanel>
    </ResizablePanelGroup>
  </div>
);

export const Vertical = () => (
  <div className="rounded-lg border" style={{ height: 240, width: 460 }}>
    <ResizablePanelGroup direction="vertical" style={{ height: '100%' }}>
      <ResizablePanel defaultSize={55} minSize={20}>
        <div className="flex h-full items-center justify-center p-4 text-sm">Session log</div>
      </ResizablePanel>
      <ResizableHandle withHandle />
      <ResizablePanel defaultSize={45} minSize={20}>
        <div className="flex h-full items-center justify-center p-4 text-sm">Fault timeline</div>
      </ResizablePanel>
    </ResizablePanelGroup>
  </div>
);
