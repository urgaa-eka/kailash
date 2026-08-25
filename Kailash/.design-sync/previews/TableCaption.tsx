import {
  Table,
  TableCaption,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from 'frontend';

// TableCaption is a <caption>; outside a <table> the browser drops it entirely,
// so both cells compose it in its parent.
export const BelowTable = () => (
  <Table>
    <TableCaption>Charging sessions recorded in the last hour.</TableCaption>
    <TableHeader>
      <TableRow>
        <TableHead>Session</TableHead>
        <TableHead className="text-right">Energy</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell className="font-medium">SES-4821</TableCell>
        <TableCell className="text-right">42.6 kWh</TableCell>
      </TableRow>
      <TableRow>
        <TableCell className="font-medium">SES-4822</TableCell>
        <TableCell className="text-right">18.1 kWh</TableCell>
      </TableRow>
    </TableBody>
  </Table>
);

export const LongerCaption = () => (
  <Table>
    <TableCaption>
      Settlement is reconciled weekly against seven OCPI peers; figures shown are
      provisional until the window closes on Sunday 23:59 IST.
    </TableCaption>
    <TableHeader>
      <TableRow>
        <TableHead>Peer</TableHead>
        <TableHead className="text-right">Owed</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow>
        <TableCell>Statiq</TableCell>
        <TableCell className="text-right">₹ 84,120</TableCell>
      </TableRow>
      <TableRow>
        <TableCell>ChargeZone</TableCell>
        <TableCell className="text-right">₹ 51,640</TableCell>
      </TableRow>
    </TableBody>
  </Table>
);
