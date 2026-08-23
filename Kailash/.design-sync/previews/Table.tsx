import {
  Table,
  TableCaption,
  TableHeader,
  TableBody,
  TableFooter,
  TableRow,
  TableHead,
  TableCell,
  Badge,
} from 'frontend';

const SESSIONS = [
  { id: 'SES-4821', station: 'Urjaa North Hub', kwh: '42.6', status: 'Completed', cost: '₹  681' },
  { id: 'SES-4822', station: 'Cyber City P2', kwh: '18.1', status: 'Charging', cost: '₹  290' },
  { id: 'SES-4823', station: 'Urjaa North Hub', kwh: '61.0', status: 'Completed', cost: '₹  976' },
  { id: 'SES-4824', station: 'Sohna Road', kwh: '7.4', status: 'Faulted', cost: '₹  118' },
];

const tone = (s: string) =>
  s === 'Faulted' ? 'destructive' : s === 'Charging' ? 'secondary' : 'outline';

export const SessionLog = () => (
  <Table>
    <TableCaption>Charging sessions recorded in the last hour.</TableCaption>
    <TableHeader>
      <TableRow>
        <TableHead>Session</TableHead>
        <TableHead>Station</TableHead>
        <TableHead>Status</TableHead>
        <TableHead className="text-right">Energy</TableHead>
        <TableHead className="text-right">Billed</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      {SESSIONS.map((s) => (
        <TableRow key={s.id}>
          <TableCell className="font-medium">{s.id}</TableCell>
          <TableCell>{s.station}</TableCell>
          <TableCell>
            <Badge variant={tone(s.status)}>{s.status}</Badge>
          </TableCell>
          <TableCell className="text-right">{s.kwh} kWh</TableCell>
          <TableCell className="text-right">{s.cost}</TableCell>
        </TableRow>
      ))}
    </TableBody>
    <TableFooter>
      <TableRow>
        <TableCell colSpan={3}>Total</TableCell>
        <TableCell className="text-right">129.1 kWh</TableCell>
        <TableCell className="text-right">₹ 2,065</TableCell>
      </TableRow>
    </TableFooter>
  </Table>
);

export const Compact = () => (
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>Department</TableHead>
        <TableHead className="text-right">Open tasks</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell className="font-medium">Grid Operations</TableCell>
        <TableCell className="text-right">14</TableCell>
      </TableRow>
      <TableRow>
        <TableCell className="font-medium">Customer Care</TableCell>
        <TableCell className="text-right">6</TableCell>
      </TableRow>
      <TableRow>
        <TableCell className="font-medium">Field Maintenance</TableCell>
        <TableCell className="text-right">23</TableCell>
      </TableRow>
    </TableBody>
  </Table>
);
