import React from 'react';
import { FileText, Plus, Download, TrendingUp, LayoutDashboard, BarChart3 } from 'lucide-react';
import { Card, CardContent } from '../components/UI/card';
import { Button } from '../components/UI/button';
import { Badge } from '../components/UI/badge';
import './Reports.css';

const Reports = () => {
    const reports = [
        { id: 1, name: 'Weekly Performance Summary', type: 'Performance', generated: '2025-11-20', status: 'ready', size: '2.4 MB' },
        { id: 2, name: 'Monthly Operations Report', type: 'Operations', generated: '2025-11-15', status: 'ready', size: '5.1 MB' },
        { id: 3, name: 'Q4 Analytics Overview', type: 'Analytics', generated: '2025-11-10', status: 'ready', size: '8.7 MB' },
        { id: 4, name: 'Department Health Check', type: 'Health', generated: '2025-11-18', status: 'processing', size: '-' },
    ];

    return (
        <div className="reports-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">
                        <FileText size={28} strokeWidth={1.5} className="inline-icon" /> Reports
                    </h1>
                    <p className="page-subtitle">Generate and download organizational reports</p>
                </div>
                <Button variant="primary" icon={Plus}>Generate Report</Button>
            </div>

            <div className="report-types">
                <Card className="report-type-card">
                    <div className="report-type-icon blue">
                        <TrendingUp size={32} strokeWidth={1.5} />
                    </div>
                    <h3>Performance Report</h3>
                    <p>Detailed analysis of department and task performance metrics</p>
                    <Button variant="secondary" size="small">Generate</Button>
                </Card>

                <Card className="report-type-card">
                    <div className="report-type-icon green">
                        <LayoutDashboard size={32} strokeWidth={1.5} />
                    </div>
                    <h3>Operations Summary</h3>
                    <p>Comprehensive overview of daily operations and activities</p>
                    <Button variant="secondary" size="small">Generate</Button>
                </Card>

                <Card className="report-type-card">
                    <div className="report-type-icon yellow">
                        <BarChart3 size={32} strokeWidth={1.5} />
                    </div>
                    <h3>Analytics Report</h3>
                    <p>Data-driven insights and trend analysis across all metrics</p>
                    <Button variant="secondary" size="small">Generate</Button>
                </Card>
            </div>

            <Card title="Recent Reports">
                <div className="reports-table-wrapper">
                    <table className="reports-table">
                        <thead>
                            <tr>
                                <th>Report Name</th>
                                <th>Type</th>
                                <th>Generated</th>
                                <th>Status</th>
                                <th>Size</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {reports.map(report => (
                                <tr key={report.id}>
                                    <td className="report-name">
                                        <FileText size={16} strokeWidth={1.5} className="inline-icon" />
                                        {report.name}
                                    </td>
                                    <td>
                                        <Badge variant="info">{report.type}</Badge>
                                    </td>
                                    <td>{report.generated}</td>
                                    <td>
                                        <Badge variant={report.status === 'ready' ? 'success' : 'warning'}>
                                            {report.status}
                                        </Badge>
                                    </td>
                                    <td>{report.size}</td>
                                    <td>
                                        {report.status === 'ready' && (
                                            <Button variant="ghost" size="small" icon={Download}>
                                                Download
                                            </Button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
};

export default Reports;
