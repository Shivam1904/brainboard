import { FrequencySettings, getFrequencyOptions } from '../../types/frequency';

interface FrequencyControlsProps {
  frequency: FrequencySettings;
  onChange: (frequency: FrequencySettings) => void;
  pillarColor?: string;
}



const FrequencyControls = ({ frequency, onChange, pillarColor = '#3B82F6' }: FrequencyControlsProps) => {
  const frequencyUnits = ['TIMES', 'HOURS'] as const;
  const frequencyPeriods = ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY'] as const;

  // Normalize so dropdown value always matches an option (API may return lowercase or wrong types)
  const rawPeriod = (frequency.frequencyPeriod || 'DAILY').toUpperCase();
  const period = (frequencyPeriods as readonly string[]).includes(rawPeriod) ? rawPeriod as typeof frequencyPeriods[number] : 'DAILY';
  const rawUnit = (frequency.frequencyUnit || 'TIMES').toUpperCase();
  const unit = (frequencyUnits as readonly string[]).includes(rawUnit) ? rawUnit as typeof frequencyUnits[number] : 'TIMES';
  const frequencyOptions = getFrequencyOptions(period);
  const amount = (() => {
    const n = Number(frequency.frequency);
    if (Number.isNaN(n) || n < frequencyOptions[0]) return frequencyOptions[0];
    if (n > frequencyOptions[frequencyOptions.length - 1]) return frequencyOptions[frequencyOptions.length - 1];
    return frequencyOptions.includes(n) ? n : frequencyOptions[0];
  })();
  
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
            id='freq-amount'     
            value={amount}
            onChange={(e) => updateFrequency({ frequency: parseInt(e.target.value, 10) })}
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
            id='freq-unit'   
            value={unit}
            onChange={(e) => updateFrequency({ frequencyUnit: e.target.value as 'TIMES' | 'HOURS' })}
            className="w-full px-3 py-2 bg-white/80 backdrop-blur-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium"
            style={{ backgroundColor: pillarColor }}
          >
            {frequencyUnits.map(u => (
              <option key={u} value={u}>{u}</option>
            ))}
          </select>
        </div>
        
        {/* Frequency Period */}
        <div>
          <label className="block text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">
            Period
          </label>
          <select
            id='freq-period'   
            value={period}  
            onChange={(e) => updateFrequency({ frequencyPeriod: e.target.value as typeof frequencyPeriods[number] })}
            className="w-full px-3 py-2 bg-white/80 backdrop-blur-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium"
            style={{ backgroundColor: pillarColor }}
          >
            {frequencyPeriods.map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-xl border border-blue-200">
        <p className="text-sm font-bold text-gray-800 text-center">
          Approx. {amount} {unit} {period}
        </p>
      </div>
    </div>
  );
};

export default FrequencyControls; 