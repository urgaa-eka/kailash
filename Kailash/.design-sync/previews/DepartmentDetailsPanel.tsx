import { DepartmentDetailsPanel } from 'frontend';

// This panel fetches its detail from REACT_APP_BACKEND_URL on mount, so a static
// capture can only ever show the pre-response state. That state is real — it is
// what an operator sees for the first few hundred milliseconds — and it is the
// honest limit of what a preview can show for a data-fetching component.
export const BeforeData = () => (
  <div className="w-[520px]">
    <DepartmentDetailsPanel
      department={{ id: 'ganesha', name: 'Grid Operations', chief: 'Ganesha' }}
      onClose={() => {}}
    />
  </div>
);
