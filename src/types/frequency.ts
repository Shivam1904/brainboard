export interface FrequencySettings {
  frequencySet: 'OCCASIONAL' | 'COMFORTABLE' | 'BALANCED' | 'RIGOROUS';
  frequencySetValue: number;
  frequency: number;
  frequencyUnit: 'TIMES' | 'HOURS';
  frequencyPeriod: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY';
  isDailyHabit: boolean;
}

// Frequency set mapping
export const getFrequencySet = (value: number): string => {
  if (value < 0.25) return 'OCCASIONAL';
  if (value < 0.50) return 'COMFORTABLE';
  if (value < 0.75) return 'BALANCED';
  return 'RIGOROUS';
};

// Get frequency options based on period
export const getFrequencyOptions = (period: string): number[] => {
  switch (period) {
    case 'DAILY': return Array.from({length: 10}, (_, i) => i + 1);
    case 'WEEKLY': return Array.from({length: 7}, (_, i) => i + 1);
    case 'MONTHLY': return Array.from({length: 4}, (_, i) => i + 1);
    case 'YEARLY': return Array.from({length: 11}, (_, i) => i + 1);
    default: return Array.from({length: 4}, (_, i) => i + 1);
  }
};

// Reverse calculation (detailed settings to slider value)
export const getReverseFrequencyValue = (settings: FrequencySettings): number => {
  let freqDaily = 0.5;
  
  switch (settings.frequencyPeriod) {
    case 'MONTHLY':
      freqDaily = settings.frequency / 28.0;
      break;
    case 'WEEKLY':
      freqDaily = settings.frequency / 7.0;
      break;
    case 'DAILY':
      freqDaily = settings.frequency;
      break;
  }
  
  return Math.min(freqDaily, 0.99);
}; 