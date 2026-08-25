import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent,
  Button,
  ChevronsUpDown,
} from 'frontend';
export const Open = () => (
  <Collapsible defaultOpen className="w-[420px] space-y-2">
    <div className="flex items-center justify-between rounded-md border px-4 py-2">
      <span className="text-sm font-semibold">Connector diagnostics</span>
      <CollapsibleTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Toggle diagnostics">
          <ChevronsUpDown />
        </Button>
      </CollapsibleTrigger>
    </div>
    <CollapsibleContent className="space-y-2">
      <div className="rounded-md border px-4 py-2 font-mono text-xs">
        CP-01 · CCS2 · handshake 1.2s · 0 retries
      </div>
      <div className="rounded-md border px-4 py-2 font-mono text-xs">
        CP-02 · CCS2 · handshake 1.4s · 0 retries
      </div>
      <div className="rounded-md border px-4 py-2 font-mono text-xs">
        CP-03 · Type 2 · handshake 2.9s · 3 retries
      </div>
    </CollapsibleContent>
  </Collapsible>
);

export const Closed = () => (
  <Collapsible className="w-[420px] space-y-2">
    <div className="flex items-center justify-between rounded-md border px-4 py-2">
      <span className="text-sm font-semibold">Raw OCPP frames</span>
      <CollapsibleTrigger asChild>
        <Button variant="ghost" size="sm">
          Show
        </Button>
      </CollapsibleTrigger>
    </div>
    <CollapsibleContent>
      <div className="rounded-md border px-4 py-2 font-mono text-xs">
        Hidden until the trigger is activated.
      </div>
    </CollapsibleContent>
  </Collapsible>
);
