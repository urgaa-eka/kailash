import React from 'react';
import { Navigate } from 'react-router-dom';
import MainLayout from './Layout/MainLayout';

const ProtectedRoute = ({ children, noLayout = false }) => {
    const token = localStorage.getItem('token');
    
    if (!token) {
        return <Navigate to="/" replace />;
    }
    
    // If noLayout is true, render children directly without MainLayout wrapper
    if (noLayout) {
        return <>{children}</>;
    }
    
    return (
        <MainLayout>
            {children}
        </MainLayout>
    );
};

export default ProtectedRoute;
