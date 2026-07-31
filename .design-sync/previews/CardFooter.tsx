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

// CardFooter is a flex row with the p-6 pt-0 gutter; shown inside a Card, which
// is the only place it has a box to sit in.
export const Actions = () => (
  <Card className="w-[380px]">
    <CardHeader>
      <CardTitle>Sohna Road</CardTitle>
      <CardDescription>Connector 3 locked out</CardDescription>
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground">
        Fault E-19 raised twice in the last hour.
      </p>
    </CardContent>
    <CardFooter className="gap-2">
      <Button>Dispatch engineer</Button>
      <Button variant="outline">Dismiss</Button>
    </CardFooter>
  </Card>
);

export const SplitRow = () => (
  <Card className="w-[380px]">
    <CardHeader>
      <CardTitle>Tariff plan</CardTitle>
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground">Time-of-day, revised 14 July.</p>
    </CardContent>
    <CardFooter className="justify-between">
      <Badge variant="secondary">Draft</Badge>
      <Button size="sm">Publish</Button>
    </CardFooter>
  </Card>
);

export const MetaOnly = () => (
  <Card className="w-[380px]">
    <CardHeader>
      <CardTitle>Weekly settlement</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-semibold">₹ 4,18,900</div>
    </CardContent>
    <CardFooter>
      <p className="text-xs text-muted-foreground">Reconciled 2 hours ago · 7 OCPI peers</p>
    </CardFooter>
  </Card>
);
