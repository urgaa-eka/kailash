import {
  Command,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
  CommandShortcut,
  Zap,
  FileText,
  Wrench,
  Search,
} from 'frontend';
// Command renders inline (cmdk, no portal) — unlike CommandDialog, which does.
export const Palette = () => (
  <Command className="w-[440px] rounded-lg border shadow-md">
    <CommandInput placeholder="Search stations, sessions, runbooks…" />
    <CommandList>
      <CommandEmpty>No results found.</CommandEmpty>
      <CommandGroup heading="Stations">
        <CommandItem>
          <Zap className="mr-2 h-4 w-4" />
          Urjaa North Hub
        </CommandItem>
        <CommandItem>
          <Zap className="mr-2 h-4 w-4" />
          Cyber City P2
        </CommandItem>
      </CommandGroup>
      <CommandSeparator />
      <CommandGroup heading="Actions">
        <CommandItem>
          <FileText className="mr-2 h-4 w-4" />
          Export weekly report
          <CommandShortcut>⌘E</CommandShortcut>
        </CommandItem>
        <CommandItem>
          <Wrench className="mr-2 h-4 w-4" />
          Raise a field ticket
          <CommandShortcut>⌘T</CommandShortcut>
        </CommandItem>
      </CommandGroup>
    </CommandList>
  </Command>
);

export const Filtered = () => (
  <Command className="w-[440px] rounded-lg border shadow-md" defaultValue="urjaa">
    <CommandInput placeholder="Type to filter…" value="urj" />
    <CommandList>
      <CommandEmpty>No results found.</CommandEmpty>
      <CommandGroup heading="Stations">
        <CommandItem value="urjaa">
          <Search className="mr-2 h-4 w-4" />
          Urjaa North Hub
        </CommandItem>
      </CommandGroup>
    </CommandList>
  </Command>
);
