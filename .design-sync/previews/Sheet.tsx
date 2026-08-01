import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
  SheetClose,
  Button,
  Label,
  Input,
  Switch,
} from 'frontend';

// Rendered open on the right edge — SheetContent is fixed-position, so a closed
// Sheet shows nothing at all.
export const Open = () => (
  <Sheet defaultOpen modal={false}>
    <SheetContent
      side="right"
      className="w-[380px] sm:max-w-[380px]"
      onOpenAutoFocus={(e) => e.preventDefault()}
    >
      <SheetHeader>
        <SheetTitle>Station settings</SheetTitle>
        <SheetDescription>Urjaa North Hub · Gurugram</SheetDescription>
      </SheetHeader>
      <div className="space-y-5 py-6">
        <div className="space-y-2">
          <Label htmlFor="sheet-name">Display name</Label>
          <Input id="sheet-name" defaultValue="Urjaa North Hub" />
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="sheet-roaming">Accept roaming</Label>
          <Switch id="sheet-roaming" defaultChecked />
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="sheet-maint">Maintenance mode</Label>
          <Switch id="sheet-maint" />
        </div>
      </div>
      <SheetFooter>
        <SheetClose asChild>
          <Button variant="outline">Cancel</Button>
        </SheetClose>
        <Button>Save</Button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
);
