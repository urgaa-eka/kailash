import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from 'frontend';

// BreadcrumbItem is an <li> with inline-flex spacing; outside a BreadcrumbList
// it has no list context, so both cells compose it in its parent.
export const LinkAndCurrent = () => (
  <Breadcrumb>
    <BreadcrumbList>
      <BreadcrumbItem>
        <BreadcrumbLink href="#">Network</BreadcrumbLink>
      </BreadcrumbItem>
      <BreadcrumbSeparator />
      <BreadcrumbItem>
        <BreadcrumbPage>Gurugram</BreadcrumbPage>
      </BreadcrumbItem>
    </BreadcrumbList>
  </Breadcrumb>
);

export const FourItems = () => (
  <Breadcrumb>
    <BreadcrumbList>
      {['Network', 'Gurugram', 'Urjaa North Hub'].map((label) => (
        <BreadcrumbItem key={label}>
          <BreadcrumbLink href="#">{label}</BreadcrumbLink>
          <BreadcrumbSeparator />
        </BreadcrumbItem>
      ))}
      <BreadcrumbItem>
        <BreadcrumbPage>Connector 3</BreadcrumbPage>
      </BreadcrumbItem>
    </BreadcrumbList>
  </Breadcrumb>
);
