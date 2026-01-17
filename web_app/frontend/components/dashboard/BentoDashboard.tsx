import React from 'react';
import { Responsive, useContainerWidth } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

import { LiveTickerWidget } from './widgets/LiveTickerWidget';
import { ConsensusChartWidget } from './widgets/ConsensusChartWidget';
import { AgentMatrixWidget } from './widgets/AgentMatrixWidget';
import { SignalTableWidget } from './widgets/SignalTableWidget';

interface BentoDashboardProps {
    swarmData: any;
    tickerData?: any;
    loading: boolean;
    onDeepDive: (data: any) => void;
    agentConfig: any;
    isPremium: boolean;
}

const DEFAULT_LAYOUTS = {
    lg: [
        { i: 'ticker', x: 0, y: 0, w: 4, h: 4 },
        { i: 'matrix', x: 4, y: 0, w: 5, h: 4 },
        { i: 'consensus', x: 9, y: 0, w: 3, h: 4 },
        { i: 'signals', x: 0, y: 4, w: 12, h: 12 }
    ]
};

export const BentoDashboard: React.FC<BentoDashboardProps> = ({ swarmData, tickerData, loading, onDeepDive, agentConfig, isPremium }) => {
    const { width, containerRef, mounted } = useContainerWidth();

    return (
        <div ref={containerRef} className="w-full h-full min-h-[800px]">
            {mounted && (
                <Responsive
                    className="layout"
                    layouts={DEFAULT_LAYOUTS}
                    width={width}
                    breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
                    cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
                    rowHeight={30}
                    margin={[16, 16]}
                    dragConfig={{ enabled: true }}
                    resizeConfig={{ enabled: true }}
                >
                    <div key="ticker" className="bg-transparent h-full">
                        {/* Use independent tickerData if available, else fallback to swarmData (which might be slower) */}
                        <LiveTickerWidget
                            data={tickerData ? { summary_data: tickerData } : swarmData}
                            loading={!tickerData && loading}
                        />
                    </div>

                    <div key="matrix" className="bg-transparent h-full">
                        <AgentMatrixWidget
                            data={swarmData?.swarm_breakdown}
                            config={agentConfig}
                            isPremium={isPremium}
                        />
                    </div>

                    <div key="consensus" className="bg-transparent h-full">
                        <ConsensusChartWidget data={swarmData} />
                    </div>

                    <div key="signals" className="bg-transparent h-full">
                        <SignalTableWidget
                            data={swarmData?.swarm_breakdown}
                            onDeepDive={onDeepDive}
                            loading={loading}
                        />
                    </div>
                </Responsive>
            )}
        </div>
    );
};
