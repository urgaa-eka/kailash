import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
} from 'frontend';

// DrawerHeader is the centred (sm:text-left) title block of vaul's fixed-position
// panel; it only has a box inside an open DrawerContent.
export const TitleAndDescription = () => (
  <Drawer defaultOpen modal={false}>
    <DrawerContent>
      <DrawerHeader>
        <DrawerTitle>Session SES-4824</DrawerTitle>
        <DrawerDescription>
          Sohna Road · connector 3 · ended with fault E-19
        </DrawerDescription>
      </DrawerHeader>
      <div className="px-4 pb-8 text-sm text-muted-foreground">
        Body content sits below the header block.
      </div>
    </DrawerContent>
  </Drawer>
);
