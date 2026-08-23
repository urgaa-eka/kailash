import {
  Popover,
  PopoverTrigger,
  PopoverContent,
  Button,
  Label,
  Input,
} from 'frontend';

// Rendered open so the floating content is on the card; the trigger stays
// visible underneath it, which is the real anchored relationship.
export const Open = () => (
  <Popover defaultOpen modal={false}>
    <PopoverTrigger asChild>
      <Button variant="outline">Output limits</Button>
    </PopoverTrigger>
    <PopoverContent className="w-80" onOpenAutoFocus={(e) => e.preventDefault()}>
      <div className="space-y-4">
        <div className="space-y-1">
          <h4 className="font-medium leading-none">Output limits</h4>
          <p className="text-sm text-muted-foreground">
            Applied to every connector at this station.
          </p>
        </div>
        <div className="grid gap-3">
          <div className="grid grid-cols-3 items-center gap-4">
            <Label htmlFor="ceil">Ceiling</Label>
            <Input id="ceil" defaultValue="60 kW" className="col-span-2 h-8" />
          </div>
          <div className="grid grid-cols-3 items-center gap-4">
            <Label htmlFor="floor">Floor</Label>
            <Input id="floor" defaultValue="7 kW" className="col-span-2 h-8" />
          </div>
        </div>
      </div>
    </PopoverContent>
  </Popover>
);
