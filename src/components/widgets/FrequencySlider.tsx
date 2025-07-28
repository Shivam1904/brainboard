import React from 'react';
import { getFrequencySet } from '../../types/frequency';

interface FrequencySliderProps {
  value: number;
  onChange: (value: number) => void;
  pillarColor?: string;
}

const FrequencySlider = ({ value, onChange, pillarColor = '#3B82F6' }: FrequencySliderProps) => {
  const points = [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1];
  const labels = ['', 'OCCASIONAL', '', 'COMFORTABLE', '', 'BALANCED', '', 'RIGOROUS', ''];
  
  return (
    <div className="w-full">
      {/* Labels */}
      <div className="flex justify-between mb-4">
        {points.map((point, index) => (
          <div 
            key={index} 
            className={`text-xs px-2 py-1 rounded-full transition-all ${
              value >= point - 0.125 && value < point + 0.124
                ? 'bg-blue-100 text-blue-800 font-bold shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {labels[index]}
          </div>
        ))}
      </div>
      
      {/* Slider */}
      <div className="relative">
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full h-3 bg-gray-200 rounded-full appearance-none cursor-pointer slider"
          style={{
            background: `linear-gradient(to right, ${pillarColor} 0%, ${pillarColor} ${value * 100}%, #e5e7eb ${value * 100}%, #e5e7eb 100%)`
          }}
        />
        
        {/* Frequency set indicator */}
        <div className="mt-3 text-center">
          <span className="inline-block px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full text-sm font-bold shadow-lg">
            {getFrequencySet(value)}
          </span>
        </div>
      </div>
    </div>
  );
};



export default FrequencySlider; 