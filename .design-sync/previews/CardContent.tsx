import { Card, CardHeader, CardTitle, CardContent, CardDescription } from 'frontend';

// CardContent contributes the p-6 pt-0 body gutter and nothing else; it is only
// legible inside a Card, so every cell composes it there.
export const Text = () => (
  <Card className="w-[380px]">
    <CardHeader>
      <CardTitle>Derating policy</CardTitle>
    </CardHeader>
    <CardContent>
      <p className="text-sm text-muted-foreground">
        Output steps down in 10 kW increments once the transformer crosses 85% of rated
        capacity, and recovers automatically after ten minutes below the threshold.
      </p>
    </CardContent>
  </Card>
);

export const Metrics = () => (
  <Card className="w-[380px]">
    <CardHeader>
      <CardTitle>Today</CardTitle>
      <CardDescription>All zones</CardDescription>
    </CardHeader>
    <CardContent className="grid grid-cols-3 gap-4">
      <div>
        <div className="text-2xl font-semibold">312</div>
        <div className="text-xs text-muted-foreground">Sessions</div>
      </div>
      <div>
        <div className="text-2xl font-semibold">6.8k</div>
        <div className="text-xs text-muted-foreground">kWh</div>
      </div>
      <div>
        <div className="text-2xl font-semibold">99.1%</div>
        <div className="text-xs text-muted-foreground">Uptime</div>
      </div>
    </CardContent>
  </Card>
);

export const NoHeader = () => (
  <Card className="w-[380px]">
    <CardContent className="pt-6">
      <p className="text-sm">
        Without a CardHeader above it the top gutter must be restored with{' '}
        <code className="rounded bg-muted px-1 py-0.5 text-xs">pt-6</code>.
      </p>
    </CardContent>
  </Card>
);
