import {
  Menubar,
  MenubarMenu,
  MenubarTrigger,
  MenubarContent,
  MenubarItem,
  MenubarSeparator,
  MenubarShortcut,
  MenubarCheckboxItem,
  MenubarLabel,
} from 'frontend';

// Menubar's Radix root takes the open menu's value, so `defaultValue` opens one
// menu without any pointer interaction.
export const WithOpenMenu = () => (
  <Menubar defaultValue="station">
    <MenubarMenu value="station">
      <MenubarTrigger>Station</MenubarTrigger>
      <MenubarContent>
        <MenubarLabel>Urjaa North Hub</MenubarLabel>
        <MenubarSeparator />
        <MenubarItem>
          Session log <MenubarShortcut>⌘L</MenubarShortcut>
        </MenubarItem>
        <MenubarItem>
          Export report <MenubarShortcut>⌘E</MenubarShortcut>
        </MenubarItem>
        <MenubarSeparator />
        <MenubarCheckboxItem checked>Show offline connectors</MenubarCheckboxItem>
      </MenubarContent>
    </MenubarMenu>
    <MenubarMenu value="grid">
      <MenubarTrigger>Grid</MenubarTrigger>
      <MenubarContent>
        <MenubarItem>Load profile</MenubarItem>
        <MenubarItem>Derating history</MenubarItem>
      </MenubarContent>
    </MenubarMenu>
    <MenubarMenu value="help">
      <MenubarTrigger>Help</MenubarTrigger>
      <MenubarContent>
        <MenubarItem>Runbooks</MenubarItem>
      </MenubarContent>
    </MenubarMenu>
  </Menubar>
);
