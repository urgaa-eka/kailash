import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from 'frontend';

export const Default = () => (
  <Accordion type="single" collapsible defaultValue="grid" className="w-[420px]">
    <AccordionItem value="grid">
      <AccordionTrigger>Grid Operations</AccordionTrigger>
      <AccordionContent>
        Load balancing across 42 stations, with automatic derating when a transformer
        crosses 85% of rated capacity.
      </AccordionContent>
    </AccordionItem>
    <AccordionItem value="care">
      <AccordionTrigger>Customer Care</AccordionTrigger>
      <AccordionContent>
        Session disputes, refunds and RFID re-issues. Escalates to Grid Operations when a
        fault code repeats at the same connector.
      </AccordionContent>
    </AccordionItem>
    <AccordionItem value="field">
      <AccordionTrigger>Field Maintenance</AccordionTrigger>
      <AccordionContent>
        Preventive schedules and on-site dispatch, driven by the anomaly service's
        connector wear model.
      </AccordionContent>
    </AccordionItem>
  </Accordion>
);

export const AllCollapsed = () => (
  <Accordion type="single" collapsible className="w-[420px]">
    <AccordionItem value="a">
      <AccordionTrigger>Tariff plans</AccordionTrigger>
      <AccordionContent>Time-of-day and flat-rate plans per zone.</AccordionContent>
    </AccordionItem>
    <AccordionItem value="b">
      <AccordionTrigger>Roaming partners</AccordionTrigger>
      <AccordionContent>OCPI peers and their settlement windows.</AccordionContent>
    </AccordionItem>
  </Accordion>
);
