
import { getFrequencySet } from '../../types/frequency';

interface FrequencySliderProps {
  value: number;
  onChange: (value: number) => void;
  pillarColor?: string;
}

const FrequencySlider = ({ value, onChange, pillarColor = '#3B82F6' }: FrequencySliderProps) => {
  const labels = ['OCCASIONAL', 'COMFORTABLE', 'BALANCED', 'RIGOROUS'];

  return (
    <div className="w-full">
      {/* Labels */}
      <div className="flex justify-between mb-4">
        {labels.map((label, index) => (
          <div
            key={index}
            className={`text-xs px-2 py-1 rounded-full transition-all ${getFrequencySet(value) == label
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

      </div>
    </div>
  );
};



export default FrequencySlider; 