import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from 'frontend';

// TableHead is a <th> and only renders inside a table's header row.
export const HeaderRow = () => (
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Session</TableHead>
        <TableHead>Station</TableHead>
        <TableHead>Status</TableHead>
        <TableHead className="text-right">Energy</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell className="font-medium">SES-4821</TableCell>
        <TableCell>Urjaa North Hub</TableCell>
        <TableCell>Completed</TableCell>
        <TableCell className="text-right">42.6 kWh</TableCell>
      </TableRow>
    </TableBody>
  </Table>
);

export const WidthConstrained = () => (
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead className="w-[120px]">Connector</TableHead>
        <TableHead>Description</TableHead>
        <TableHead className="w-[100px] text-right">Retries</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell className="font-mono text-xs">CP-03</TableCell>
        <TableCell>Type 2 AC · handshake exceeded 2.5s threshold</TableCell>
        <TableCell className="text-right">3</TableCell>
      </TableRow>
      <TableRow>
        <TableCell className="font-mono text-xs">CP-01</TableCell>
        <TableCell>CCS2 · nominal</TableCell>
        <TableCell className="text-right">0</TableCell>
      </TableRow>
    </TableBody>
  </Table>
);
