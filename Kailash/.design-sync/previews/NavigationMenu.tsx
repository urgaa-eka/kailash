import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuTrigger,
  NavigationMenuContent,
  NavigationMenuLink,
} from 'frontend';

// Radix NavigationMenu takes the open item's value on the root, so `defaultValue`
// opens a panel without any hover interaction.
export const WithOpenPanel = () => (
  <NavigationMenu defaultValue="network">
    <NavigationMenuList>
      <NavigationMenuItem value="network">
        <NavigationMenuTrigger>Network</NavigationMenuTrigger>
        <NavigationMenuContent>
          <ul className="grid w-[420px] gap-3 p-4 md:grid-cols-2">
            {[
              ['Stations', '42 sites across four zones'],
              ['Connectors', 'CCS2, Type 2 AC and CHAdeMO'],
              ['Grid load', 'Live transformer headroom'],
              ['Roaming', 'OCPI peers and settlement'],
            ].map(([title, desc]) => (
              <li key={title}>
                <NavigationMenuLink className="block rounded-md p-3 hover:bg-accent">
                  <div className="text-sm font-medium">{title}</div>
                  <p className="text-sm text-muted-foreground">{desc}</p>
                </NavigationMenuLink>
              </li>
            ))}
          </ul>
        </NavigationMenuContent>
      </NavigationMenuItem>
      <NavigationMenuItem value="ops">
        <NavigationMenuTrigger>Operations</NavigationMenuTrigger>
        <NavigationMenuContent>
          <ul className="grid w-[280px] gap-3 p-4">
            <li>
              <NavigationMenuLink className="block rounded-md p-3 hover:bg-accent">
                <div className="text-sm font-medium">Runbooks</div>
              </NavigationMenuLink>
            </li>
          </ul>
        </NavigationMenuContent>
      </NavigationMenuItem>
    </NavigationMenuList>
  </NavigationMenu>
);
