import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuItem,
  DropdownMenuGroup,
  DropdownMenuSeparator,
  Button,
} from 'frontend';

// DropdownMenuLabel is a non-interactive heading inside the menu surface; it has
// no box of its own, so it is composed inside an open DropdownMenu.
export const SectionHeadings = () => (
  <DropdownMenu defaultOpen modal={false}>
    <DropdownMenuTrigger asChild>
      <Button variant="outline">Filters</Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start" className="w-56">
      <DropdownMenuLabel>Zone</DropdownMenuLabel>
      <DropdownMenuGroup>
        <DropdownMenuItem>Gurugram</DropdownMenuItem>
        <DropdownMenuItem>Cyber City</DropdownMenuItem>
      </DropdownMenuGroup>
      <DropdownMenuSeparator />
      <DropdownMenuLabel>Connector</DropdownMenuLabel>
      <DropdownMenuGroup>
        <DropdownMenuItem>CCS2</DropdownMenuItem>
        <DropdownMenuItem>Type 2 AC</DropdownMenuItem>
      </DropdownMenuGroup>
    </DropdownMenuContent>
  </DropdownMenu>
);
