import {
  Button,
  Zap,
  Plus,
  Trash2,
  ArrowRight,
} from 'frontend';
export const Variants = () => (
  <div className="flex flex-wrap items-center gap-3">
    <Button>Start charging</Button>
    <Button variant="secondary">View sessions</Button>
    <Button variant="outline">Export report</Button>
    <Button variant="ghost">Cancel</Button>
    <Button variant="destructive">Stop session</Button>
    <Button variant="link">Read the runbook</Button>
  </div>
);

export const Sizes = () => (
  <div className="flex flex-wrap items-center gap-3">
    <Button size="sm">Small</Button>
    <Button size="default">Default</Button>
    <Button size="lg">Large</Button>
    <Button size="icon" aria-label="Add station">
      <Plus />
    </Button>
  </div>
);

export const WithIcons = () => (
  <div className="flex flex-wrap items-center gap-3">
    <Button>
      <Zap />
      Provision charger
    </Button>
    <Button variant="outline">
      Continue
      <ArrowRight />
    </Button>
    <Button variant="destructive">
      <Trash2 />
      Decommission
    </Button>
  </div>
);

export const Disabled = () => (
  <div className="flex flex-wrap items-center gap-3">
    <Button disabled>Start charging</Button>
    <Button variant="secondary" disabled>
      View sessions
    </Button>
    <Button variant="outline" disabled>
      Export report
    </Button>
  </div>
);
