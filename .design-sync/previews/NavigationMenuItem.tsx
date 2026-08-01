import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuTrigger,
  NavigationMenuContent,
  NavigationMenuLink,
} from 'frontend';

// NavigationMenuItem is an <li> in the Radix menu; it needs the root and list
// around it, and one item is opened with the root's defaultValue.
export const ThreeItems = () => (
  <NavigationMenu defaultValue="ops">
    <NavigationMenuList>
      <NavigationMenuItem value="network">
        <NavigationMenuTrigger>Network</NavigationMenuTrigger>
        <NavigationMenuContent>
          <ul className="w-[260px] p-4">
            <li className="text-sm text-muted-foreground">Stations and connectors</li>
          </ul>
        </NavigationMenuContent>
      </NavigationMenuItem>
      <NavigationMenuItem value="ops">
        <NavigationMenuTrigger>Operations</NavigationMenuTrigger>
        <NavigationMenuContent>
          <ul className="grid w-[300px] gap-2 p-4">
            {['Runbooks', 'Rollback', 'Staging'].map((t) => (
              <li key={t}>
                <NavigationMenuLink className="block rounded-md p-2 text-sm hover:bg-accent">
                  {t}
                </NavigationMenuLink>
              </li>
            ))}
          </ul>
        </NavigationMenuContent>
      </NavigationMenuItem>
      <NavigationMenuItem value="reports">
        <NavigationMenuTrigger>Reports</NavigationMenuTrigger>
        <NavigationMenuContent>
          <ul className="w-[260px] p-4">
            <li className="text-sm text-muted-foreground">Weekly settlement</li>
          </ul>
        </NavigationMenuContent>
      </NavigationMenuItem>
    </NavigationMenuList>
  </NavigationMenu>
);
