import { Skeleton, Card, CardContent, CardHeader } from 'frontend';

export const CardPlaceholder = () => (
  <Card className="w-[380px]">
    <CardHeader className="space-y-2">
      <Skeleton className="h-4 w-40" />
      <Skeleton className="h-3 w-56" />
    </CardHeader>
    <CardContent className="space-y-2">
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-2/3" />
    </CardContent>
  </Card>
);

export const ListPlaceholder = () => (
  <div className="w-[420px] space-y-4">
    {[0, 1, 2].map((i) => (
      <div key={i} className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-3 w-1/2" />
          <Skeleton className="h-3 w-1/3" />
        </div>
      </div>
    ))}
  </div>
);

export const Shapes = () => (
  <div className="flex items-center gap-4">
    <Skeleton className="h-12 w-12 rounded-full" />
    <Skeleton className="h-12 w-24 rounded-md" />
    <Skeleton className="h-12 w-40" />
  </div>
);
