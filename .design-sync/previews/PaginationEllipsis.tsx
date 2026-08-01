import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationEllipsis,
} from 'frontend';

// PaginationEllipsis is a bare glyph standing in for skipped page numbers; only
// legible between two PaginationLinks.
export const BetweenPages = () => (
  <Pagination>
    <PaginationContent>
      <PaginationItem>
        <PaginationLink href="#">1</PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationEllipsis />
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#" isActive>
          15
        </PaginationLink>
      </PaginationItem>
      <PaginationItem>
        <PaginationEllipsis />
      </PaginationItem>
      <PaginationItem>
        <PaginationLink href="#">42</PaginationLink>
      </PaginationItem>
    </PaginationContent>
  </Pagination>
);
