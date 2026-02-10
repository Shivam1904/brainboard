import React from 'react';
import PlanToday from './PlanToday';

interface PlannerProps {
    date: string;
    isPlanning?: boolean;
    onStartPlanning?: () => void;
    onEndPlanning: () => void;
}

const Planner = ({ date, isPlanning, onStartPlanning, onEndPlanning }: PlannerProps) => {
    // Use props if provided, otherwise fallback to local state (though we intend to always provide them from NewDashboard)
    // To simplifiy, we assume NewDashboard is the primary user and provides props.

    if (isPlanning) {
        return <PlanToday date={date} onClose={onEndPlanning} />;
    }

    return (
        <div className="flex flex-col items-center justify-center gap-6">
            <h2 className="text-2xl font-semibold text-foreground/80">Plan Your Day</h2>
            <div className="flex gap-4">
                <button
                    className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium shadow-sm active:scale-95 transform duration-100"
                    onClick={() => onStartPlanning?.()}
                >
                    Plan Today
                </button>
                <button
                    className="px-6 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors font-medium shadow-sm active:scale-95 transform duration-100"
                    onClick={() => { }}
                >
                    Auto Plan
                </button>
            </div>
        </div>
    );
};

export default Planner;
