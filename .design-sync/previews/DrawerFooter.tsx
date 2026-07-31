import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerFooter,
  DrawerClose,
  Button,
} from 'frontend';

// DrawerFooter stacks its actions full width at the bottom of the panel; shown
// inside an open Drawer, which is the only place it renders.
export const StackedActions = () => (
  <Drawer defaultOpen modal={false}>
    <DrawerContent>
      <DrawerHeader>
        <DrawerTitle>Raise a field ticket</DrawerTitle>
      </DrawerHeader>
      <div className="px-4 text-sm text-muted-foreground">
        Connector 3 will stay locked out until an engineer clears it on site.
      </div>
      <DrawerFooter>
        <Button>Dispatch engineer</Button>
        <DrawerClose asChild>
          <Button variant="outline">Cancel</Button>
        </DrawerClose>
      </DrawerFooter>
    </DrawerContent>
  </Drawer>
);
