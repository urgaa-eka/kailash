import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Button,
  Badge,
} from 'frontend';

export const Default = () => (
  <Card className="w-[380px]">
    <CardHeader>
      <CardTitle>Urjaa North Hub</CardTitle>
      <CardDescription>Gurugram · 12 DC fast chargers</CardDescription>
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground">
        Peak load held at 78% through the evening window. No thermal derating events in
        the last 24 hours.
      </p>
    </CardContent>
    <CardFooter className="gap-2">
      <Button>Open station</Button>
      <Button variant="outline">Session log</Button>
    </CardFooter>
  </Card>
);

export const WithStats = () => (
  <Card className="w-[380px]">
    <CardHeader className="flex-row items-start justify-between space-y-0">
      <div className="space-y-1.5">
        <CardTitle>Energy dispatched</CardTitle>
        <CardDescription>Last 7 days, all zones</CardDescription>
      </div>
      <Badge variant="secondary">Live</Badge>
    </CardHeader>
    <CardContent>
      <div className="text-3xl font-semibold tracking-tight">48,210 kWh</div>
      <p className="mt-1 text-sm text-muted-foreground">+12.4% against the prior week</p>
    </CardContent>
  </Card>
);

export const ContentOnly = () => (
  <Card className="w-[380px]">
    <CardContent className="pt-6">
      <p className="text-sm">
        A bare card with no header or footer — the shape used for inline panels inside a
        dashboard column.
      </p>
    </CardContent>
  </Card>
);
