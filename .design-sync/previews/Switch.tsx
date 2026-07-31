import { Switch, Label } from 'frontend';

export const States = () => (
  <div className="space-y-3">
    <div className="flex items-center space-x-2">
      <Switch id="s-on" defaultChecked />
      <Label htmlFor="s-on">On</Label>
    </div>
    <div className="flex items-center space-x-2">
      <Switch id="s-off" />
      <Label htmlFor="s-off">Off</Label>
    </div>
    <div className="flex items-center space-x-2">
      <Switch id="s-dis" disabled />
      <Label htmlFor="s-dis">Disabled</Label>
    </div>
    <div className="flex items-center space-x-2">
      <Switch id="s-dis-on" defaultChecked disabled />
      <Label htmlFor="s-dis-on">Disabled, on</Label>
    </div>
  </div>
);

export const SettingsRows = () => (
  <div className="w-[420px] divide-y rounded-md border">
    {[
      ['Automatic derating', 'Step output down above 85% transformer load', true],
      ['Roaming (OCPI)', 'Accept sessions from partner networks', true],
      ['Maintenance mode', 'Reject new sessions at this station', false],
    ].map(([title, desc, on]) => (
      <div key={title as string} className="flex items-center justify-between gap-4 p-4">
        <div className="space-y-0.5">
          <Label className="text-sm">{title}</Label>
          <p className="text-xs text-muted-foreground">{desc}</p>
        </div>
        <Switch defaultChecked={on as boolean} />
      </div>
    ))}
  </div>
);
