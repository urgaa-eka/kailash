import { ErrorBoundary, Card, CardHeader, CardTitle, CardContent } from 'frontend';

// ErrorBoundary is a class component that renders its children until one throws.
// Both states are shown, and the caught state is produced by a child that really
// throws — the fallback UI cannot be reached any other way.
const Boom = () => {
  throw new Error('Failed to load station telemetry (ECONNREFUSED 127.0.0.1:8000)');
};

export const Healthy = () => (
  <ErrorBoundary>
    <Card className="w-[380px]">
      <CardHeader>
        <CardTitle>Urjaa North Hub</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        Children render untouched while no descendant throws.
      </CardContent>
    </Card>
  </ErrorBoundary>
);

export const Caught = () => (
  <ErrorBoundary>
    <Boom />
  </ErrorBoundary>
);
