import { Pagination, PaginationContent, PaginationItem, PaginationLink } from 'frontend';

export const ActiveAndInactive = () => (
  <Pagination>
    <PaginationContent>
      <PaginationItem>
        <PaginationLink href="#">1</PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#" isActive>
          2
        </PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#">3</PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#">4</PaginationLink>
      </PaginationItem>
    </PaginationContent>
  </Pagination>
);

// Both links are active so each one draws its outline — otherwise the inactive
// `default` link renders as a bare numeral and the size axis is invisible next
// to the boxed `icon` link.
export const Sizes = () => (
  <Pagination>
    <PaginationContent className="items-center gap-3">
      <PaginationItem>
        <PaginationLink href="#" size="default" isActive>
          Page 7
        </PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#" size="icon" isActive>
          8
        </PaginationLink>
      </PaginationItem>
    </PaginationContent>
  </Pagination>
);
