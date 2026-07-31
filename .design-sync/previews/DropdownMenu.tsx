import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuCheckboxItem,
  Button,
  MoreHorizontal,
} from 'frontend';
// Rendered open: the menu is a fixed-position portal, so a closed DropdownMenu
// would show only the trigger button.
export const Open = () => (
  <DropdownMenu defaultOpen modal={false}>
    <DropdownMenuTrigger asChild>
      <Button variant="outline" size="icon" aria-label="Station actions">
        <MoreHorizontal />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start" className="w-56">
      <DropdownMenuLabel>Station actions</DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuItem>
        Open session log
        <DropdownMenuShortcut>⌘L</DropdownMenuShortcut>
      </DropdownMenuItem>
      <DropdownMenuItem>
        Export report
        <DropdownMenuShortcut>⌘E</DropdownMenuShortcut>
      </DropdownMenuItem>
      <DropdownMenuCheckboxItem checked>Show offline connectors</DropdownMenuCheckboxItem>
      <DropdownMenuSeparator />
      <DropdownMenuItem className="text-destructive focus:text-destructive">
        Decommission station
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
);
