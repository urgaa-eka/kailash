import {
  ToggleGroup,
  ToggleGroupItem,
  Bold,
  Italic,
  Underline,
} from 'frontend';
// ToggleGroupItem reads the group's variant/size context, so it is always
// composed inside <ToggleGroup>.
export const SingleSelection = () => (
  <ToggleGroup type="single" defaultValue="week">
    <ToggleGroupItem value="day">Day</ToggleGroupItem>
    <ToggleGroupItem value="week">Week</ToggleGroupItem>
    <ToggleGroupItem value="month">Month</ToggleGroupItem>
  </ToggleGroup>
);

export const MultipleSelection = () => (
  <ToggleGroup type="multiple" defaultValue={['ccs2', 'type2']}>
    <ToggleGroupItem value="ccs2">CCS2</ToggleGroupItem>
    <ToggleGroupItem value="type2">Type 2 AC</ToggleGroupItem>
    <ToggleGroupItem value="chademo">CHAdeMO</ToggleGroupItem>
  </ToggleGroup>
);

export const OutlineVariant = () => (
  <ToggleGroup type="single" variant="outline" defaultValue="b">
    <ToggleGroupItem value="a" aria-label="Bold">
      <Bold />
    </ToggleGroupItem>
    <ToggleGroupItem value="b" aria-label="Italic">
      <Italic />
    </ToggleGroupItem>
    <ToggleGroupItem value="c" aria-label="Underline">
      <Underline />
    </ToggleGroupItem>
  </ToggleGroup>
);

export const Sizes = () => (
  <div className="flex flex-col items-start gap-3">
    <ToggleGroup type="single" size="sm" defaultValue="a">
      <ToggleGroupItem value="a">Small</ToggleGroupItem>
      <ToggleGroupItem value="b">Group</ToggleGroupItem>
    </ToggleGroup>
    <ToggleGroup type="single" size="lg" defaultValue="a">
      <ToggleGroupItem value="a">Large</ToggleGroupItem>
      <ToggleGroupItem value="b">Group</ToggleGroupItem>
    </ToggleGroup>
  </div>
);
