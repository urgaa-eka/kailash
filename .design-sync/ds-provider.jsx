// Preview/runtime wrapper for the Kailash AI design system.
//
// Several components in src/components read react-router context (Link,
// useNavigate, useLocation, Navigate) and the Radix tooltip context. In the
// real app those come from <BrowserRouter> in src/index.js and a
// <TooltipProvider> in the app shell. This module supplies the same contexts
// so a component can render standalone in a preview card or a generated
// design. It adds no styling and no behaviour of its own.
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { TooltipProvider } from '@/components/UI/tooltip';

export const DesignSystemProvider = ({ children, initialPath = '/' }) => (
  <MemoryRouter initialEntries={[initialPath]}>
    <TooltipProvider delayDuration={0}>{children}</TooltipProvider>
  </MemoryRouter>
);

export default DesignSystemProvider;
