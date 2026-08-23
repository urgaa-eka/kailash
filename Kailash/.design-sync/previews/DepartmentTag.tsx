import { DepartmentTag } from 'frontend';

export const Departments = () => (
  <div className="flex flex-wrap items-center gap-3">
    <DepartmentTag departmentName="Grid Operations" />
    <DepartmentTag departmentName="Customer Care" />
    <DepartmentTag departmentName="Field Maintenance" />
  </div>
);

export const WithPosition = () => (
  <div className="flex flex-wrap items-center gap-3">
    <DepartmentTag departmentName="Grid Operations" position="Chief" />
    <DepartmentTag departmentName="Settlement" position="Lead" />
  </div>
);
