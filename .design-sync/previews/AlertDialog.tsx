import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from 'frontend';

// Rendered open — the confirmation state is the whole point of the component,
// and AlertDialogContent is a fixed-position portal.
export const Open = () => (
  <AlertDialog defaultOpen>
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Stop all sessions at Sohna Road?</AlertDialogTitle>
        <AlertDialogDescription>
          Four drivers are charging right now. They will be billed for the energy already
          delivered and asked to unplug. This cannot be undone.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>Keep charging</AlertDialogCancel>
        <AlertDialogAction>Stop all sessions</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
);
