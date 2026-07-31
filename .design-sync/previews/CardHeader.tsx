import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge } from 'frontend';

// CardHeader has no visual of its own outside a Card — it contributes the
// flex-column layout and the p-6 gutter. Every cell composes it in its parent.
export const TitleAndDescription = () => (
  <Card className="w-[380px]">
    <CardHeader>
      <CardTitle>Urjaa North Hub</CardTitle>
      <CardDescription>Gurugram · 12 DC fast chargers</CardDescription>
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground">Header above ordinary card content.</p>
    </CardContent>
  </Card>
);

export const WithTrailingAction = () => (
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
    </CardContent>
  </Card>
);

export const TitleOnly = () => (
  <Card className="w-[380px]">
    <CardHeader>
      <CardTitle>Fault queue</CardTitle>
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground">
        A header carrying only a title still reserves its full p-6 gutter.
      </p>
    </CardContent>
  </Card>
);
