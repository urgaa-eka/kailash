import { MainLayout, Card, CardHeader, CardTitle, CardContent } from 'frontend';

// The authenticated app shell: sidebar plus header plus a content slot.
export const WithContent = () => (
  <MainLayout>
    <Card>
      <CardHeader>
        <CardTitle>Grid Operations</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        Page content renders inside the shell's content slot.
      </CardContent>
    </Card>
  </MainLayout>
);
