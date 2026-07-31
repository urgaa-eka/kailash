import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
  Button,
  Input,
  Label,
} from 'frontend';

// Rendered open: DialogContent is a fixed-position portal, so a closed Dialog
// would show an empty card. cfg.overrides pins this to a single-story card.
export const Open = () => (
  <Dialog defaultOpen modal={false}>
    {/* Radix focuses the first field on open, which paints a text selection over
        the captured card; the dialog is still fully keyboard-reachable. */}
    <DialogContent className="sm:max-w-[440px]" onOpenAutoFocus={(e) => e.preventDefault()}>
      <DialogHeader>
        <DialogTitle>Decommission connector</DialogTitle>
        <DialogDescription>
          CP-03 at Sohna Road will stop accepting sessions immediately. Existing sessions
          are allowed to finish.
        </DialogDescription>
      </DialogHeader>
      <div className="space-y-2 py-2">
        <Label htmlFor="reason">Reason</Label>
        <Input id="reason" defaultValue="Repeat fault E-19" />
      </div>
      <DialogFooter>
        <DialogClose asChild>
          <Button variant="outline">Cancel</Button>
        </DialogClose>
        <Button variant="destructive">Decommission</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
);
