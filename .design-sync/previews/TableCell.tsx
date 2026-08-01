import {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableRow,
  TableHead,
  TableCell,
  Badge,
} from 'frontend';

// TableCell is a <td>; a bare <td> outside a table is not rendered at all, so
// every cell composes it inside its Table.
export const Alignment = () => (
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Session</TableHead>
        <TableHead>Station</TableHead>
        <TableHead className="text-right">Energy</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell className="font-medium">SES-4821</TableCell>
        <TableCell>Urjaa North Hub</TableCell>
        <TableCell className="text-right">42.6 kWh</TableCell>
      </TableRow>
      <TableRow>
        <TableCell className="font-medium">SES-4823</TableCell>
        <TableCell>Cyber City P2</TableCell>
        <TableCell className="text-right">61.0 kWh</TableCell>
      </TableRow>
    </TableBody>
  </Table>
);

export const RichContent = () => (
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Connector</TableHead>
        <TableHead>Status</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell className="font-mono text-xs">CP-01</TableCell>
        <TableCell>
          <Badge variant="outline">Available</Badge>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell className="font-mono text-xs">CP-03</TableCell>
        <TableCell>
          <Badge variant="destructive">Faulted</Badge>
        </TableCell>
      </TableRow>
    </TableBody>
  </Table>
);

export const Spanning = () => (
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Zone</TableHead>
        <TableHead>Sessions</TableHead>
        <TableHead className="text-right">Billed</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell>Gurugram</TableCell>
        <TableCell>128</TableCell>
        <TableCell className="text-right">₹ 1,84,200</TableCell>
      </TableRow>
    </TableBody>
    <TableFooter>
      <TableRow>
        <TableCell colSpan={2}>Total</TableCell>
        <TableCell className="text-right">₹ 1,84,200</TableCell>
      </TableRow>
    </TableFooter>
  </Table>
);
