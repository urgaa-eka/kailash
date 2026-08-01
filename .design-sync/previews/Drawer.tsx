import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
  DrawerFooter,
  DrawerClose,
  Button,
} from 'frontend';

// vaul's Drawer is fixed to the bottom edge; rendered open so the card shows the
// component rather than an empty trigger.
export const Open = () => (
  <Drawer defaultOpen modal={false}>
    <DrawerContent>
      <DrawerHeader>
        <DrawerTitle>Session SES-4824</DrawerTitle>
        <DrawerDescription>Sohna Road · connector 3 · ended with fault E-19</DrawerDescription>
      </DrawerHeader>
      <div className="grid grid-cols-3 gap-4 px-4 pb-2 text-center">
        <div>
          <div className="text-2xl font-semibold">7.4</div>
          <div className="text-xs text-muted-foreground">kWh</div>
        </div>
        <div>
          <div className="text-2xl font-semibold">11m</div>
          <div className="text-xs text-muted-foreground">Duration</div>
        </div>
        <div>
          <div className="text-2xl font-semibold">₹ 118</div>
          <div className="text-xs text-muted-foreground">Billed</div>
        </div>
      </div>
      <DrawerFooter>
        <Button>Raise a field ticket</Button>
        <DrawerClose asChild>
          <Button variant="outline">Close</Button>
        </DrawerClose>
      </DrawerFooter>
    </DrawerContent>
  </Drawer>
);
