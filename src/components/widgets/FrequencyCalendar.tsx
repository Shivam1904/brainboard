import React from 'react';
import { FrequencySettings } from '../../types/frequency';

interface FrequencyCalendarProps {
  frequency: FrequencySettings;
  pillarColor?: string;
}

const FrequencyCalendar = ({ frequency }: FrequencyCalendarProps) => {
  // Generate days for 7 months centered around current month
  const generateYearDays = () => {
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth();
    const currentYear = currentDate.getFullYear();
    const days = [];

    // Calculate start and end months (3 past, current, 3 future)
    const startMonth = Math.max(0, currentMonth - 3);
    const endMonth = Math.min(11, currentMonth + 3);

    // Start from the first day of the start month
    const startDate = new Date(currentYear, startMonth, 1);

    // End on the last day of the end month
    const endDate = new Date(currentYear, endMonth + 1, 0);

    // Generate days for the 7-month period
    for (let i = 0; i <= (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24); i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      days.push(date);
    }

    return days;
  };

  // Convert slider value (0-1) to frequency based on period
  const getFrequencyFromSlider = (): number => {
    const sliderValue = frequency.frequencySetValue; // 0-1

    switch (frequency.frequencyPeriod) {
      case 'DAILY':
        // 0-1 maps to 0-10 times daily
        return sliderValue * 10;

      case 'WEEKLY':
        // 0-1 maps to 0-7 days weekly
        return sliderValue * 7;

      case 'MONTHLY':
        // 0-1 maps to 0-31 days monthly
        return sliderValue * 31;

      case 'YEARLY':
        // 0-1 maps to 0-365 days yearly
        return sliderValue * 365;

      default:
        return sliderValue * 7; // Default to weekly
    }
  };

  // Get biased frequency with minimal randomization only on last day of period
  const getBiasedFrequency = (): number => {
    const baseFrequency = getFrequencyFromSlider();

    if (frequency.frequencyPeriod === 'DAILY') {
      // No randomization for daily
      return baseFrequency;
    }

    return baseFrequency + [1, 0, -1][Math.floor(Math.random() * 3)];
  };

  // Check if a specific day should have activity based on frequency settings
  const shouldHaveActivity = (date: Date): boolean => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const checkDate = new Date(date);
    checkDate.setHours(0, 0, 0, 0);

    if (checkDate < today) return false; // Past dates

    const biasedFrequency = getBiasedFrequency(date);

    switch (frequency.frequencyPeriod) {
      case 'DAILY':
        return true; // Every future day is active

      case 'WEEKLY': {
        // Day of week: 1 = Monday, 2 = Tuesday, ..., 7 = Sunday
        const dayOfWeek = date.getDay() === 0 ? 7 : date.getDay(); // Convert Sunday from 0 to 7
        return biasedFrequency >= dayOfWeek;
      }

      case 'MONTHLY': {
        // Day of month: 1, 2, 3, ..., 31
        const dayOfMonth = date.getDate();
        return biasedFrequency >= dayOfMonth;
      }

      case 'YEARLY': {
        // Day of year: 1, 2, 3, ..., 365
        const startOfYear = new Date(date.getFullYear(), 0, 0);
        const dayOfYear = Math.floor((date.getTime() - startOfYear.getTime()) / (1000 * 60 * 60 * 24)) + 1;
        return biasedFrequency >= dayOfYear;
      }

      default:
        return false;
    }
  };

  // Get heatmap color based on activity status
  const getHeatmapColor = (date: Date): string => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const checkDate = new Date(date);
    checkDate.setHours(0, 0, 0, 0);

    if (checkDate < today) return 'bg-gray-100'; // Past dates (Gray80)
    if (checkDate.getTime() === today.getTime()) return 'bg-yellow-200'; // Today (Yellow180)

    const hasActivity = shouldHaveActivity(date);
    return hasActivity ? 'bg-green-400' : 'bg-gray-300'; // DARKGREEN60 vs Gray40
  };



  // Group days by weeks for the grid layout
  const groupDaysByWeeks = (days: Date[]) => {
    const weeks: (Date | null)[][] = [];
    let currentWeek: (Date | null)[] = [];

    days.forEach((day, index) => {
      // Add empty cells for days before the first day of the year
      if (index === 0 && day.getDay() > 0) {
        for (let i = 0; i < day.getDay(); i++) {
          currentWeek.push(null);
        }
      }

      currentWeek.push(day);

      // Start new week on Sunday
      if (day.getDay() === 6 || index === days.length - 1) {
        weeks.push([...currentWeek]);
        currentWeek = [];
      }
    });

    return weeks;
  };

  const yearDays = generateYearDays();
  const weeks = groupDaysByWeeks(yearDays);

  const isToday = (date: Date): boolean => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-sm font-bold text-gray-800 mb-2">
          7-Month Frequency Heatmap
        </h3>
        <p className="text-xs text-gray-600">
          {frequency.frequency} {frequency.frequencyUnit.toLowerCase()} {frequency.frequencyPeriod.toLowerCase()}
        </p>
      </div>

      {/* Heatmap grid */}
      <div className="flex">
        {/* Day labels */}
        <div className="flex flex-col mr-2 space-y-1">
          {['', 'Mon', '', 'Wed', '', 'Fri', ''].map((day, index) => (
            <div key={index} className="text-xs text-gray-500 h-3 flex items-center">
              {day}
            </div>
          ))}
        </div>

        {/* Heatmap squares */}
        <div className="flex-1">
          <div className="flex space-x-1">
            {weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col space-y-1">
                {week.map((day: Date | null, dayIndex: number) => {
                  if (!day) {
                    return <div key={dayIndex} className="w-3 h-3" />;
                  }

                  const hasActivity = shouldHaveActivity(day);
                  const heatmapColor = getHeatmapColor(day);

                  return (
                    <div
                      key={dayIndex}
                      className={`w-3 h-3 rounded-sm transition-all ${heatmapColor} ${isToday(day) ? 'ring-1 ring-blue-500' : ''
                        }`}
                      title={`${day.toLocaleDateString()}: ${hasActivity ? 'Active' : 'No activity'}`}
                    />
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Month labels */}
      <div className="flex mt-2 ml-8">
        {(() => {
          const currentDate = new Date();
          const currentMonth = currentDate.getMonth();
          const startMonth = Math.max(0, currentMonth - 3);
          const endMonth = Math.min(11, currentMonth + 3);

          const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
          const visibleMonths = [];

          for (let i = startMonth; i <= endMonth; i++) {
            visibleMonths.push(monthNames[i]);
          }
          return visibleMonths.map((month) => (
            <div key={month} className="text-xs text-gray-500" style={{ width: `${100 / visibleMonths.length}%` }}>
              {month}
            </div>
          ));
        })()}
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center space-x-4 text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-gray-100 rounded-sm"></div>
          <span className="text-gray-600">Past</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-yellow-200 rounded-sm"></div>
          <span className="text-gray-600">Today</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-400 rounded-sm"></div>
          <span className="text-gray-600">Active</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-gray-300 rounded-sm"></div>
          <span className="text-gray-600">Inactive</span>
        </div>
      </div>
    </div>
  );
};

export default FrequencyCalendar; 