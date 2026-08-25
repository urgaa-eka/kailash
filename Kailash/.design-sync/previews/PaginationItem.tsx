import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
} from 'frontend';

// PaginationItem is an <li>; it needs the PaginationContent list around it to
// take part in the flex row.
export const InRow = () => (
  <Pagination>
    <PaginationContent>
      <PaginationItem>
        <PaginationPrevious href="#" />
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#">4</PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#" isActive>
          5
        </PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#">6</PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationNext href="#" />
      </PaginationItem>
    </PaginationContent>
  </Pagination>
);

export const SinglePage = () => (
  <Pagination>
    <PaginationContent>
      <PaginationItem>
        <PaginationLink href="#" isActive>
          1
        </PaginationLink>
      </PaginationItem>
    </PaginationContent>
  </Pagination>
);
