import {
  Menubar,
  MenubarMenu,
  MenubarTrigger,
  MenubarContent,
  MenubarLabel,
  MenubarItem,
  MenubarSeparator,
} from 'frontend';

// MenubarLabel is a heading inside an open menu surface — composed in its parent,
// which is the only place it renders.
export const InOpenMenu = () => (
  <Menubar defaultValue="zone">
    <MenubarMenu value="zone">
      <MenubarTrigger>Zone</MenubarTrigger>
      <MenubarContent>
        <MenubarLabel>North</MenubarLabel>
        <MenubarItem>Gurugram</MenubarItem>
        <MenubarItem>Cyber City</MenubarItem>
        <MenubarSeparator />
        <MenubarLabel>West</MenubarLabel>
        <MenubarItem>Manesar</MenubarItem>
      </MenubarContent>
    </MenubarMenu>
  </Menubar>
);
