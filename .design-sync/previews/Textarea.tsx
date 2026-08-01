import { Textarea, Label, Button } from 'frontend';

export const Default = () => (
  <div className="w-[420px] space-y-2">
    <Label htmlFor="incident">Incident summary</Label>
    {/* rows sized to the copy: the default min-h-[60px] clips a third line. */}
    <Textarea
      id="incident"
      rows={4}
      defaultValue={
        'Connector 3 raised fault E-19 twice within the hour. Session SES-4824 terminated at 7.4 kWh. Locked out pending a field inspection.'
      }
    />
  </div>
);

export const Placeholder = () => (
  <div className="w-[420px] space-y-2">
    <Label htmlFor="note">Handover note</Label>
    <Textarea id="note" placeholder="What should the next shift know?" />
  </div>
);

export const Disabled = () => (
  <div className="w-[420px]">
    <Textarea defaultValue="Read-only once the incident is closed." disabled />
  </div>
);

export const WithSubmit = () => (
  <div className="w-[420px] space-y-2">
    <Label htmlFor="reply">Reply to operator</Label>
    <Textarea id="reply" placeholder="Type your reply…" />
    <div className="flex justify-end">
      <Button size="sm">Send</Button>
    </div>
  </div>
);
