import { Tabs, TabsList, TabsTrigger, TabsContent, Card, CardContent } from 'frontend';

export const Default = () => (
  <Tabs defaultValue="sessions" className="w-[460px]">
    <TabsList>
      <TabsTrigger value="sessions">Sessions</TabsTrigger>
      <TabsTrigger value="faults">Faults</TabsTrigger>
      <TabsTrigger value="settlement">Settlement</TabsTrigger>
    </TabsList>
    <TabsContent value="sessions">
      <Card>
        <CardContent className="pt-6 text-sm text-muted-foreground">
          312 sessions today across all zones, 6.8 MWh dispatched.
        </CardContent>
      </Card>
    </TabsContent>
    <TabsContent value="faults">
      <Card>
        <CardContent className="pt-6 text-sm text-muted-foreground">
          Three open faults; one connector locked out at Sohna Road.
        </CardContent>
      </Card>
    </TabsContent>
    <TabsContent value="settlement">
      <Card>
        <CardContent className="pt-6 text-sm text-muted-foreground">
          Weekly window closes Sunday 23:59 IST across seven OCPI peers.
        </CardContent>
      </Card>
    </TabsContent>
  </Tabs>
);

export const TwoTabs = () => (
  <Tabs defaultValue="grid" className="w-[380px]">
    <TabsList className="grid w-full grid-cols-2">
      <TabsTrigger value="grid">Grid load</TabsTrigger>
      <TabsTrigger value="demand">Demand</TabsTrigger>
    </TabsList>
    <TabsContent value="grid" className="pt-3 text-sm text-muted-foreground">
      Peak 78% at 19:40, no derating events.
    </TabsContent>
    <TabsContent value="demand" className="pt-3 text-sm text-muted-foreground">
      Forecast 7.4 MWh for tomorrow, +9% week on week.
    </TabsContent>
  </Tabs>
);

export const WithDisabledTab = () => (
  <Tabs defaultValue="overview" className="w-[460px]">
    <TabsList>
      <TabsTrigger value="overview">Overview</TabsTrigger>
      <TabsTrigger value="audit">Audit log</TabsTrigger>
      <TabsTrigger value="billing" disabled>
        Billing
      </TabsTrigger>
    </TabsList>
    <TabsContent value="overview" className="pt-3 text-sm text-muted-foreground">
      Billing is disabled until the operator completes KYC.
    </TabsContent>
  </Tabs>
);
