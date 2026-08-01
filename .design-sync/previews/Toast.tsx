import {
  ToastProvider,
  Toast,
  ToastTitle,
  ToastDescription,
  ToastAction,
  ToastClose,
  ToastViewport,
} from 'frontend';

// Driven directly through ToastProvider rather than the useToast store, so the
// toast is present at capture time. ToastViewport is fixed-position, hence the
// single-story card override. ToastViewport is normally fixed to the screen
// corner, which lands outside a captured card, so the cells place it in flow.
export const Default = () => (
  <ToastProvider duration={1000000}>
    <Toast open>
      <div className="grid gap-1">
        <ToastTitle>Station saved</ToastTitle>
        <ToastDescription>Urjaa North Hub now accepts roaming sessions.</ToastDescription>
      </div>
      <ToastClose />
    </Toast>
    <ToastViewport className="static flex-col gap-2 p-0" />
  </ToastProvider>
);

export const Destructive = () => (
  <ToastProvider duration={1000000}>
    <Toast open variant="destructive">
      <div className="grid gap-1">
        <ToastTitle>Connector locked out</ToastTitle>
        <ToastDescription>CP-03 raised fault E-19 twice in the last hour.</ToastDescription>
      </div>
      <ToastAction altText="Dispatch an engineer">Dispatch</ToastAction>
      <ToastClose />
    </Toast>
    <ToastViewport className="static flex-col gap-2 p-0" />
  </ToastProvider>
);
