# Kailash AI design system — how to build with it

A Tailwind + shadcn/ui ("new-york") system for the Go4Garage / Urjaa EV charging
network. Components are the app's own, compiled from `frontend/src/components`.

## Wrap the tree in `DesignSystemProvider`

Six components read react-router context (`Header`, `LegalFooter`, `Sidebar`,
`CookieConsent`, `ProtectedRoute`, `SessionTimeout`), and the tooltip parts read
Radix's tooltip context. Without the wrapper those throw or render nothing:

```jsx
const { DesignSystemProvider, Button } = window.KailashDS;

<DesignSystemProvider>
  <Button>Start charging</Button>
</DesignSystemProvider>
```

Everything else renders bare. There is no theme provider and no dark-mode
toggle to wire up — tokens are plain CSS custom properties on `:root`.

## Style with Tailwind utilities over the token layer

This is a Tailwind system. Compose layout with ordinary utilities
(`flex`, `grid`, `gap-4`, `space-y-2`, `rounded-md`, `p-6`) and reach for the
**semantic token utilities** for anything with colour, so the result tracks the
brand instead of hard-coding hexes:

| Family | Utilities |
| --- | --- |
| Surfaces | `bg-background`, `bg-card`, `bg-popover`, `bg-muted`, `bg-accent` |
| Text | `text-foreground`, `text-muted-foreground`, `text-card-foreground`, `text-primary`, `text-destructive` |
| Intent fills | `bg-primary` / `text-primary-foreground`, `bg-secondary` / `text-secondary-foreground`, `bg-destructive` / `text-destructive-foreground`, `bg-accent` / `text-accent-foreground` |
| Lines & focus | `border`, `border-input`, `ring-ring`, `outline-none` |
| Radius | `rounded-sm` / `rounded-md` / `rounded-lg` (all derive from `--radius`) |

Brand colours are also addressable directly when a semantic token is not the
right fit — `hsl(var(--g4g-purple))`, `--g4g-green`, `--g4g-bright-green`,
`--g4g-orange`, `--g4g-purple-light`, `--g4g-text-gray`, `--g4g-gray`. Use them
through arbitrary values, e.g.
`className="text-[hsl(var(--g4g-purple))]"`, which is exactly how the app's own
branded components do it. There are named Tailwind colours too — `g4g-blue`,
`g4g-steel-grey`, `g4g-electric-yellow`, `g4g-graphite`, `cool-grey`,
`dark-slate`, `highlight-teal`, `error-red` — used by the investor-dashboard
components.

`primary` renders `#5F0386` (brand purple), `secondary` `#3E7E45` (green), and
`accent` `#0BD566` (bright green). Type is Inter, code is JetBrains Mono, both
loaded from Google Fonts by `styles.css`.

> **Use the token names, not hex values.** The hexes above are what the tokens
> actually paint, and they differ slightly from the hexes written in the source
> comments (`#570683`, `#417E46`, `#0DA34E`) — the declared HSL triples and their
> comments disagree for 8 of the 11 brand tokens. Always write `bg-primary` /
> `text-primary` / `hsl(var(--g4g-purple))` rather than pasting a hex, so your
> work tracks the token if it is ever corrected.
>
> One practical consequence: `accent` is much brighter than its comment suggests,
> and `accent-foreground` is white — only 1.96:1 against it. Use `bg-accent` as a
> highlight fill (selected rows, active triggers), as the components already do,
> not behind small text.

## Prefer variants over restyling

Most primitives carry `cva` variants — pass the variant instead of overriding
classes. `Button` has `variant` (`default`, `destructive`, `outline`,
`secondary`, `ghost`, `link`) and `size` (`default`, `sm`, `lg`, `icon`);
`Badge` and `Alert` have their own `variant` sets; `Toggle` and `ToggleGroup`
take `variant` and `size`. Each component's `<Name>.d.ts` lists its exact union.

Compound components come as parts and must be composed: `Card` +
`CardHeader`/`CardTitle`/`CardDescription`/`CardContent`/`CardFooter`, `Table` +
`TableHeader`/`TableBody`/`TableRow`/`TableHead`/`TableCell`, `Dialog` +
`DialogContent`/`DialogHeader`/`DialogTitle`/`DialogFooter`, and so on. A part
used outside its parent renders nothing or throws.

## Where the truth is

- `styles.css` and the stylesheet it imports carry every token definition and
  all component CSS — read it before inventing a colour.
- `components/<group>/<Name>/<Name>.prompt.md` carries each component's prop
  contract; `<Name>.d.ts` is the same contract as TypeScript.
- The dashboard components (`EnhancedKPICard`, `DataSourceBadge`,
  `AutomationBadge`, `ProblemResolutionCard`, `AIImpactSummary`) are designed
  against a **dark** surface — place them on one, e.g. `bg-[#1a1a2e]`.

## An idiomatic composition

```jsx
const { DesignSystemProvider, Card, CardHeader, CardTitle, CardDescription,
        CardContent, CardFooter, Button, Badge } = window.KailashDS;

<DesignSystemProvider>
  <div className="grid grid-cols-2 gap-4 p-6">
    <Card>
      <CardHeader className="flex-row items-start justify-between space-y-0">
        <div className="space-y-1.5">
          <CardTitle>Urjaa North Hub</CardTitle>
          <CardDescription>Gurugram · 12 DC fast chargers</CardDescription>
        </div>
        <Badge variant="secondary">Live</Badge>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-semibold tracking-tight">48,210 kWh</div>
        <p className="mt-1 text-sm text-muted-foreground">+12.4% week on week</p>
      </CardContent>
      <CardFooter className="gap-2">
        <Button>Open station</Button>
        <Button variant="outline">Session log</Button>
      </CardFooter>
    </Card>
  </div>
</DesignSystemProvider>
```
