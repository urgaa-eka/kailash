import {
  Toggle,
  Bold,
  Italic,
  Underline,
  Bell,
  Zap,
} from 'frontend';
export const States = () => (
  <div className="flex items-center gap-3">
    <Toggle aria-label="Off">Off</Toggle>
    <Toggle defaultPressed aria-label="On">
      On
    </Toggle>
    <Toggle disabled aria-label="Disabled">
      Disabled
    </Toggle>
  </div>
);

export const Variants = () => (
  <div className="flex items-center gap-3">
    <Toggle aria-label="Default variant">Default</Toggle>
    <Toggle variant="outline" aria-label="Outline variant">
      Outline
    </Toggle>
    <Toggle variant="outline" defaultPressed aria-label="Outline pressed">
      Outline, on
    </Toggle>
  </div>
);

export const Sizes = () => (
  <div className="flex items-center gap-3">
    <Toggle size="sm" aria-label="Small">
      <Bold />
    </Toggle>
    <Toggle size="default" defaultPressed aria-label="Default">
      <Italic />
    </Toggle>
    <Toggle size="lg" aria-label="Large">
      <Underline />
    </Toggle>
  </div>
);

export const InContext = () => (
  <div className="flex items-center gap-3">
    <Toggle variant="outline" defaultPressed aria-label="Alerts on">
      <Bell className="mr-2 h-4 w-4" />
      Alerts
    </Toggle>
    <Toggle variant="outline" aria-label="Fast charging filter">
      <Zap className="mr-2 h-4 w-4" />
      Fast charging only
    </Toggle>
  </div>
);
