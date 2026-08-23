import { Separator } from 'frontend';

export const Horizontal = () => (
  <div className="w-[420px]">
    <div className="space-y-1">
      <h4 className="text-sm font-semibold leading-none">Kailash AI</h4>
      <p className="text-sm text-muted-foreground">
        20 departments orchestrating the Go4Garage charging network.
      </p>
    </div>
    <Separator className="my-4" />
    <div className="flex h-5 items-center space-x-4 text-sm">
      <span>Docs</span>
      <Separator orientation="vertical" />
      <span>Runbooks</span>
      <Separator orientation="vertical" />
      <span>Status</span>
    </div>
  </div>
);

export const InList = () => (
  <div className="w-[420px] rounded-md border">
    {['Grid Operations', 'Customer Care', 'Field Maintenance'].map((d, i, a) => (
      <div key={d}>
        <div className="px-4 py-3 text-sm">{d}</div>
        {i < a.length - 1 ? <Separator /> : null}
      </div>
    ))}
  </div>
);
