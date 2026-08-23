import { AppLayout, Card, CardContent } from 'frontend';

export const WithTitle = () => (
  <AppLayout title="Station detail">
    <Card>
      <CardContent className="pt-6 text-sm text-muted-foreground">
        Urjaa North Hub · 12 DC fast chargers
      </CardContent>
    </Card>
  </AppLayout>
);

export const WithBackButton = () => (
  <AppLayout title="Session SES-4824" showBackButton showMenuButton={false}>
    <Card>
      <CardContent className="pt-6 text-sm text-muted-foreground">
        A detail page opts into the back affordance and drops the menu button.
      </CardContent>
    </Card>
  </AppLayout>
);
