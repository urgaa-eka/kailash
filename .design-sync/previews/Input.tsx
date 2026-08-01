import { Input, Label, Button } from 'frontend';

export const Default = () => (
  <div className="w-[380px] space-y-2">
    <Label htmlFor="station">Station name</Label>
    <Input id="station" defaultValue="Urjaa North Hub" />
  </div>
);

export const Types = () => (
  <div className="w-[380px] space-y-4">
    <div className="space-y-2">
      <Label htmlFor="op-email">Operator email</Label>
      <Input id="op-email" type="email" placeholder="ops@go4garage.in" />
    </div>
    <div className="space-y-2">
      <Label htmlFor="op-pass">Password</Label>
      <Input id="op-pass" type="password" defaultValue="passphrase" />
    </div>
    <div className="space-y-2">
      <Label htmlFor="cap">Rated capacity (kW)</Label>
      <Input id="cap" type="number" defaultValue={60} />
    </div>
  </div>
);

export const States = () => (
  <div className="w-[380px] space-y-4">
    <Input placeholder="Search sessions…" />
    <Input defaultValue="SES-4821" readOnly />
    <Input defaultValue="Locked while a session is active" disabled />
  </div>
);

export const WithAction = () => (
  <div className="flex w-[380px] items-center gap-2">
    <Input placeholder="Connector id" />
    <Button>Look up</Button>
  </div>
);
