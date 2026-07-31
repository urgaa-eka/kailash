import {
  Alert,
  AlertTitle,
  AlertDescription,
  Info,
  AlertTriangle,
} from 'frontend';
export const Default = () => (
  <Alert className="w-[460px]">
    <Info className="h-4 w-4" />
    <AlertTitle>Scheduled maintenance</AlertTitle>
    <AlertDescription>
      Sohna Road goes offline for firmware updates on Sunday between 02:00 and 04:00 IST.
    </AlertDescription>
  </Alert>
);

export const Destructive = () => (
  <Alert variant="destructive" className="w-[460px]">
    <AlertTriangle className="h-4 w-4" />
    <AlertTitle>Connector fault</AlertTitle>
    <AlertDescription>
      SES-4824 ended with fault code E-19. The connector has been locked out pending a
      field inspection.
    </AlertDescription>
  </Alert>
);

export const TitleOnly = () => (
  <Alert className="w-[460px]">
    <Info className="h-4 w-4" />
    <AlertTitle>All 42 stations are reporting healthy.</AlertTitle>
  </Alert>
);
