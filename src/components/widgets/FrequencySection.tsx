import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import FrequencySlider from './FrequencySlider';
import FrequencyCalendar from './FrequencyCalendar';
import FrequencyControls from './FrequencyControls';
import { FrequencySettings, getFrequencySet, getReverseFrequencyValue } from '../../types/frequency';

interface FrequencySectionProps {
  frequency: FrequencySettings;
  onChange: (frequency: FrequencySettings) => void;
  pillarColor?: string;
}



const FrequencySection = ({ frequency, onChange, pillarColor = '#3B82F6' }: FrequencySectionProps) => {
  const [expanded, setExpanded] = useState(false);
  
  const handleSliderChange = (value: number) => {
    const frequencySet = getFrequencySet(value) as FrequencySettings['frequencySet'];
    const newFrequency = { ...frequency, frequencySetValue: value, frequencySet };
    
    // Auto-adjust detailed settings based on slider
    switch (frequencySet) {
      case 'OCCASIONAL':
        newFrequency.frequency = 2;
        newFrequency.frequencyPeriod = 'MONTHLY';
        newFrequency.isDailyHabit = false;
        break;
      case 'COMFORTABLE':
        newFrequency.frequency = 1;
        newFrequency.frequencyPeriod = 'WEEKLY';
        newFrequency.isDailyHabit = false;
        break;
      case 'BALANCED':
        newFrequency.frequency = 3;
        newFrequency.frequencyPeriod = 'WEEKLY';
        newFrequency.isDailyHabit = false;
        break;
      case 'RIGOROUS':
        newFrequency.frequency = 1;
        newFrequency.frequencyPeriod = 'DAILY';
        newFrequency.isDailyHabit = true;
        break;
    }
    
    onChange(newFrequency);
  };
  
  const handleDetailedChange = (newFrequency: FrequencySettings) => {
    // Update slider value based on detailed settings
    const sliderValue = getReverseFrequencyValue(newFrequency);
    const frequencySet = getFrequencySet(sliderValue) as FrequencySettings['frequencySet'];
    
    onChange({
      ...newFrequency,
      frequencySetValue: sliderValue,
      frequencySet
    });
  };
  
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200/50">
      {/* Header */}
      <div className="flex justify-between items-center p-4 border-b border-gray-200/50">
        <div className="flex items-center space-x-3">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: pillarColor }}></div>
          <h3 className="text-lg font-bold text-gray-800">Frequency Settings</h3>
        </div>
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
      </div>
      
      {/* Slider */}
      <div className="p-4">
        <FrequencySlider
          value={frequency.frequencySetValue}
          onChange={handleSliderChange}
          pillarColor={pillarColor}
        />
      </div>
      
      {/* Expanded Details */}
      {expanded && (
        <div className="border-t border-gray-200/50">
          {/* Calendar */}
          <div className="p-4 border-b border-gray-200/50">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
              Calendar Preview
            </h4>
            <FrequencyCalendar
              frequency={frequency}
              pillarColor={pillarColor}
            />
          </div>
          
          {/* Detailed Controls */}
          <div className="p-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <span className="w-2 h-2 rounded-full bg-blue-500 mr-2"></span>
              Detailed Settings
            </h4>
            <FrequencyControls
              frequency={frequency}
              onChange={handleDetailedChange}
              pillarColor={pillarColor}
            />
          </div>
        </div>
      )}
      
      {/* Collapsed Summary */}
      {!expanded && (
        <div className="px-4 pb-4">
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-3 rounded-lg border border-gray-200/50">
            <p className="text-sm font-medium text-gray-700 text-center">
              {frequency.frequency} {frequency.frequencyUnit} {frequency.frequencyPeriod}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FrequencySection; 