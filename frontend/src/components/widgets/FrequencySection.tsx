import { useState } from 'react';
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
    <div className="rounded-lg border border-slate-200 bg-white/80">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-200/70">
        <div className="flex items-center gap-2">
          <div
            className="w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: pillarColor }}
          />
          <h3 className="text-xs font-semibold tracking-wide text-slate-600 uppercase">
            Frequency settings
          </h3>
        </div>
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
        >
          {expanded ? (
            <span className="inline-flex items-center gap-1">
              <ChevronUp size={14} />
              Details
            </span>
          ) : (
            <span className="inline-flex items-center gap-1">
              <ChevronDown size={14} />
              Details
            </span>
          )}
        </button>
      </div>

      {/* Slider */}
      <div className="px-3 pt-3 pb-2">
        <FrequencySlider
          value={frequency.frequencySetValue}
          onChange={handleSliderChange}
          pillarColor={pillarColor}
        />
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="border-t border-slate-200/70">
          {/* Calendar */}
          <div className="px-3 py-3 border-b border-slate-200/70">
            <h4 className="text-xs font-semibold text-slate-600 mb-2 flex items-center">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-2" />
              Calendar preview
            </h4>
            <FrequencyCalendar
              frequency={frequency}
              pillarColor={pillarColor}
            />
          </div>

          {/* Detailed Controls */}
          <div className="px-3 py-3">
            <h4 className="text-xs font-semibold text-slate-600 mb-2 flex items-center">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-2" />
              Detailed settings
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
        <div className="px-3 pb-3">
          <div className="bg-slate-50 border border-slate-200/80 px-3 py-2 rounded-md">
            <p className="text-xs font-medium text-slate-700 text-center">
              {frequency.frequency} {frequency.frequencyUnit} {frequency.frequencyPeriod}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FrequencySection; 