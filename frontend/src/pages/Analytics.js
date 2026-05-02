import React from 'react';
import { BarChart3, TrendingUp, Activity, CheckCircle, Clock, Target } from 'lucide-react';
import { Card, CardContent } from '../components/UI/card';
import { Badge } from '../components/UI/badge';
import { SquareKPICard, KPIGrid } from '../components/KPICards';
import './Analytics.css';

const Analytics = () => {
    return (
        <div className="analytics-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">
                        <BarChart3 size={28} strokeWidth={1.5} className="inline-icon" /> Analytics
                    </h1>
                    <p className="page-subtitle">Performance metrics and insights</p>
                </div>
                <Badge variant="info">Last 30 Days</Badge>
            </div>

            {/* Square KPI Cards Grid */}
            <KPIGrid columns={4} className="mb-6">
                <SquareKPICard
                    label="Total Tasks"
                    value="1,234"
                    change="+12%"
                    isPositive={true}
                    icon={BarChart3}
                    color="blue"
                />
                <SquareKPICard
                    label="Completed"
                    value="892"
                    change="+8%"
                    isPositive={true}
                    icon={CheckCircle}
                    color="green"
                />
                <SquareKPICard
                    label="In Progress"
                    value="256"
                    change="-3%"
                    isPositive={false}
                    icon={Clock}
                    color="orange"
                />
                <SquareKPICard
                    label="Success Rate"
                    value="94.2%"
                    change="+2.1%"
                    isPositive={true}
                    icon={Target}
                    color="purple"
                />
            </KPIGrid>

            <div className="analytics-grid">
                <Card title="Department Performance" className="chart-card">
                    <div className="chart-placeholder">
                        <BarChart3 size={48} strokeWidth={1} />
                        <p>Chart visualization coming soon</p>
                    </div>
                </Card>
                <Card title="Task Completion Trend" className="chart-card">
                    <div className="chart-placeholder">
                        <TrendingUp size={48} strokeWidth={1} />
                        <p>Chart visualization coming soon</p>
                    </div>
                </Card>
            </div>

            <Card title="Top Performers">
                <div className="performers-list">
                    <div className="performer-item">
                        <span className="rank">1</span>
                        <span className="name">Operations</span>
                        <Badge variant="success">95% completion</Badge>
                    </div>
                    <div className="performer-item">
                        <span className="rank">2</span>
                        <span className="name">Engineering</span>
                        <Badge variant="success">92% completion</Badge>
                    </div>
                    <div className="performer-item">
                        <span className="rank">3</span>
                        <span className="name">Support</span>
                        <Badge variant="info">88% completion</Badge>
                    </div>
                    <div className="performer-item">
                        <span className="rank">4</span>
                        <span className="name">Analytics</span>
                        <Badge variant="info">85% completion</Badge>
                    </div>
                </div>
            </Card>
        </div>
    );
};

export default Analytics;
