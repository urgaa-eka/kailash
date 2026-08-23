import { DepartmentCard } from 'frontend';

// `department` is the record the dashboard passes straight through:
// { id, name, chief, role, activeTasks, workload, status }.
const GRID = {
  id: 'ganesha',
  name: 'Grid Operations',
  chief: 'Ganesha',
  role: 'Load balancing & derating',
  activeTasks: 14,
  workload: 72,
  status: 'active',
};

const FIELD = {
  id: 'hanuman',
  name: 'Field Maintenance',
  chief: 'Hanuman',
  role: 'Preventive schedules & dispatch',
  activeTasks: 23,
  workload: 41,
  status: 'idle',
};

export const Default = () => (
  <div className="w-[360px]">
    <DepartmentCard department={GRID} onClick={() => {}} />
  </div>
);

export const Active = () => (
  <div className="w-[360px]">
    <DepartmentCard department={GRID} onClick={() => {}} isActive />
  </div>
);

export const List = () => (
  <div className="w-[360px] space-y-1">
    <DepartmentCard department={GRID} onClick={() => {}} isActive />
    <DepartmentCard department={FIELD} onClick={() => {}} />
  </div>
);
