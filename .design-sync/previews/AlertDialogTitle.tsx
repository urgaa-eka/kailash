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

// AlertDialogTitle forwards to Radix's DialogTitle, which throws
// "`DialogTitle` must be used within `Dialog`" outside its root — so it is
// composed inside an open AlertDialog, the only place it renders.
export const InDialog = () => (
  <AlertDialog defaultOpen>
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Stop all sessions at Sohna Road?</AlertDialogTitle>
        <AlertDialogDescription>
          The title is the dialog's accessible name as well as its heading.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>Keep charging</AlertDialogCancel>
        <AlertDialogAction>Stop all sessions</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
);
