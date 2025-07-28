import React from 'react';
import { FrequencySettings, getFrequencyOptions } from '../../types/frequency';

interface FrequencyControlsProps {
  frequency: FrequencySettings;
  onChange: (frequency: FrequencySettings) => void;
  pillarColor?: string;
}



const FrequencyControls = ({ frequency, onChange, pillarColor = '#3B82F6' }: FrequencyControlsProps) => {
  const frequencyOptions = getFrequencyOptions(frequency.frequencyPeriod);
  const frequencyUnits = ['TIMES', 'HOURS'];
  const frequencyPeriods = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY'];
  
  const updateFrequency = (updates: Partial<FrequencySettings>) => {
    const newFrequency = { ...frequency, ...updates };
    
    // Ensure frequency is within valid range for new period
    if (updates.frequencyPeriod) {
      const maxFreq = getFrequencyOptions(updates.frequencyPeriod).length;
      newFrequency.frequency = Math.min(newFrequency.frequency, maxFreq);
    }
    
    // Update isDailyHabit flag
    newFrequency.isDailyHabit = newFrequency.frequencyPeriod === 'DAILY';
    
    onChange(newFrequency);
  };
  
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        {/* Frequency Amount */}
        <div>
          <label className="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">
            Amount
          </label>
          <select
            value={frequency.frequency}
            onChange={(e) => updateFrequency({ frequency: parseInt(e.target.value) })}
            className="w-full px-3 py-2 bg-white/80 backdrop-blur-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium"
          >
            {frequencyOptions.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        
        {/* Frequency Unit */}
        <div>
          <label className="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">
            Unit
          </label>
          <select
            value={frequency.frequencyUnit}
            onChange={(e) => updateFrequency({ frequencyUnit: e.target.value as 'TIMES' | 'HOURS' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium text-white"
            style={{ backgroundColor: pillarColor }}
          >
            {frequencyUnits.map(unit => (
              <option key={unit} value={unit}>{unit}</option>
            ))}
          </select>
        </div>
        
        {/* Frequency Period */}
        <div>
          <label className="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">
            Period
          </label>
          <select
            value={frequency.frequencyPeriod}
            onChange={(e) => updateFrequency({ frequencyPeriod: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium text-white"
            style={{ backgroundColor: pillarColor }}
          >
            {frequencyPeriods.map(period => (
              <option key={period} value={period}>{period}</option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-xl border border-blue-200">
        <p className="text-sm font-bold text-gray-800 text-center">
          Approx. {frequency.frequency} {frequency.frequencyUnit} {frequency.frequencyPeriod}
        </p>
      </div>
    </div>
  );
};

export default FrequencyControls; 