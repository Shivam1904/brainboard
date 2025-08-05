import React, { useState } from 'react';

// Base interface for all AI chat components
export interface AiChatComponent {
  id: string;
  type: string;
  props: Record<string, any>;
}

// Component props interfaces
export interface TodoFormProps {
  onSubmit: (data: { title: string; description: string }) => void;
  onCancel: () => void;
}

export interface NameChangeProps {
  currentName: string;
  onAccept: () => void;
  onCancel: () => void;
}

export interface ConfirmationProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export interface DataDisplayProps {
  title: string;
  data: any;
  onAction?: (action: string, data: any) => void;
}

export interface ProgressTrackerProps {
  current: number;
  total: number;
  label: string;
  onComplete: () => void;
}

export interface QuickActionsProps {
  actions: Array<{
    id: string;
    label: string;
    icon: string;
    action: string;
  }>;
  onAction: (actionId: string) => void;
}

export interface AlarmFormProps {
  filledParams: Record<string, any>;
  missingParams: string[];
  onSubmit: (data: Record<string, any>) => void;
  onCancel: () => void;
}

// Todo Form Component
export const TodoFormComponent: React.FC<TodoFormProps> = ({ onSubmit, onCancel }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onSubmit({ title: title.trim(), description: description.trim() });
    }
  };

  return (
    <div className="bg-muted/50 rounded-lg p-3 border">
      <h4 className="text-sm font-medium mb-2">Create New Todo</h4>
      <form onSubmit={handleSubmit} className="space-y-2">
        <input
          type="text"
          placeholder="Todo title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-2 py-1 text-xs border rounded focus:outline-none focus:ring-1 focus:ring-primary"
          required
        />
        <textarea
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-2 py-1 text-xs border rounded focus:outline-none focus:ring-1 focus:ring-primary resize-none"
          rows={2}
        />
        <div className="flex gap-2">
          <button
            type="submit"
            className="px-3 py-1 bg-primary text-primary-foreground text-xs rounded hover:bg-primary/90 transition-colors"
          >
            Save Todo
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1 bg-secondary text-secondary-foreground text-xs rounded hover:bg-secondary/80 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

// Name Change Component
export const NameChangeComponent: React.FC<NameChangeProps> = ({ currentName, onAccept, onCancel }) => {
  return (
    <div className="bg-muted/50 rounded-lg p-3 border">
      <h4 className="text-sm font-medium mb-2">Change Name</h4>
      <p className="text-xs text-muted-foreground mb-3">
        Current name: <span className="font-medium">{currentName}</span>
      </p>
      <div className="flex gap-2">
        <button
          onClick={onAccept}
          className="px-3 py-1 bg-primary text-primary-foreground text-xs rounded hover:bg-primary/90 transition-colors"
        >
          Change Name
        </button>
        <button
          onClick={onCancel}
          className="px-3 py-1 bg-secondary text-secondary-foreground text-xs rounded hover:bg-secondary/80 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

// Confirmation Component
export const ConfirmationComponent: React.FC<ConfirmationProps> = ({ message, onConfirm, onCancel }) => {
  return (
    <div className="bg-muted/50 rounded-lg p-3 border">
      <p className="text-sm mb-3">{message}</p>
      <div className="flex gap-2">
        <button
          onClick={onConfirm}
          className="px-3 py-1 bg-primary text-primary-foreground text-xs rounded hover:bg-primary/90 transition-colors"
        >
          Confirm
        </button>
        <button
          onClick={onCancel}
          className="px-3 py-1 bg-secondary text-secondary-foreground text-xs rounded hover:bg-secondary/80 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

// Data Display Component
export const DataDisplayComponent: React.FC<DataDisplayProps> = ({ title, data, onAction }) => {
  return (
    <div className="bg-muted/50 rounded-lg p-3 border">
      <h4 className="text-sm font-medium mb-2">{title}</h4>
      <div className="text-xs text-muted-foreground mb-2">
        {typeof data === 'object' ? JSON.stringify(data, null, 2) : data}
      </div>
      {onAction && (
        <button
          onClick={() => onAction('view', data)}
          className="px-3 py-1 bg-secondary text-secondary-foreground text-xs rounded hover:bg-secondary/80 transition-colors"
        >
          View Details
        </button>
      )}
    </div>
  );
};

// Progress Tracker Component
export const ProgressTrackerComponent: React.FC<ProgressTrackerProps> = ({ current, total, label, onComplete }) => {
  const percentage = Math.round((current / total) * 100);

  return (
    <div className="bg-muted/50 rounded-lg p-3 border">
      <h4 className="text-sm font-medium mb-2">{label}</h4>
      <div className="mb-2">
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>Progress</span>
          <span>{percentage}%</span>
        </div>
        <div className="w-full bg-secondary rounded-full h-2">
          <div 
            className="bg-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>
      <div className="text-xs text-muted-foreground mb-2">
        {current} of {total} completed
      </div>
      {current === total && (
        <button
          onClick={onComplete}
          className="px-3 py-1 bg-primary text-primary-foreground text-xs rounded hover:bg-primary/90 transition-colors"
        >
          Complete
        </button>
      )}
    </div>
  );
};

// Quick Actions Component
export const QuickActionsComponent: React.FC<QuickActionsProps> = ({ actions, onAction }) => {
  return (
    <div className="bg-muted/50 rounded-lg p-3 border">
      <h4 className="text-sm font-medium mb-2">Quick Actions</h4>
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction(action.id)}
            className="flex items-center gap-2 px-3 py-2 bg-secondary text-secondary-foreground text-xs rounded hover:bg-secondary/80 transition-colors"
          >
            <span>{action.icon}</span>
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

// Alarm Form Component
export const AlarmFormComponent: React.FC<AlarmFormProps> = ({ filledParams, missingParams, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<Record<string, any>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (Object.keys(formData).length > 0) {
      onSubmit(formData);
    }
  };

  const handleInputChange = (param: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [param]: value
    }));
  };

  const getParamLabel = (param: string) => {
    const labels: Record<string, string> = {
      'title': 'Alarm Title',
      'time': 'Alarm Time',
      'date': 'Alarm Date',
      'description': 'Description',
      'repeat': 'Repeat'
    };
    return labels[param] || param;
  };

  const getParamType = (param: string) => {
    if (param === 'time') return 'time';
    if (param === 'date') return 'date';
    if (param === 'description') return 'textarea';
    return 'text';
  };

  return (
    <div className="bg-muted/50 rounded-lg p-3 border">
      <h4 className="text-sm font-medium mb-2">Complete Alarm Details</h4>
      
      {/* Show filled parameters */}
      {Object.keys(filledParams).length > 0 && (
        <div className="mb-3">
          <p className="text-xs text-muted-foreground mb-1">Already provided:</p>
          <div className="space-y-1">
            {Object.entries(filledParams).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2 text-xs">
                <span className="text-green-600">✓</span>
                <span className="font-medium">{getParamLabel(key)}:</span>
                <span className="text-muted-foreground">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Form for missing parameters */}
      <form onSubmit={handleSubmit} className="space-y-2">
        {missingParams.map((param) => {
          const inputType = getParamType(param);
          const label = getParamLabel(param);
          
          return (
            <div key={param}>
              <label className="block text-xs font-medium mb-1">{label} *</label>
              {inputType === 'textarea' ? (
                <textarea
                  value={formData[param] || ''}
                  onChange={(e) => handleInputChange(param, e.target.value)}
                  className="w-full px-2 py-1 text-xs border rounded focus:outline-none focus:ring-1 focus:ring-primary resize-none"
                  rows={2}
                  required
                />
              ) : (
                <input
                  type={inputType}
                  value={formData[param] || ''}
                  onChange={(e) => handleInputChange(param, e.target.value)}
                  className="w-full px-2 py-1 text-xs border rounded focus:outline-none focus:ring-1 focus:ring-primary"
                  required
                />
              )}
            </div>
          );
        })}
        
        <div className="flex gap-2 pt-2">
          <button
            type="submit"
            disabled={Object.keys(formData).length === 0}
            className="px-3 py-1 bg-primary text-primary-foreground text-xs rounded hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Save Alarm
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1 bg-secondary text-secondary-foreground text-xs rounded hover:bg-secondary/80 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

// Component registry
export const AI_CHAT_COMPONENTS = {
  'todo-form': TodoFormComponent,
  'name-change': NameChangeComponent,
  'confirmation': ConfirmationComponent,
  'data-display': DataDisplayComponent,
  'progress-tracker': ProgressTrackerComponent,
  'quick-actions': QuickActionsComponent,
  'alarm-form': AlarmFormComponent,
} as const;

// Component renderer
export const renderAiChatComponent = (
  component: AiChatComponent,
  onAction: (componentId: string, action: string, data: any) => void
) => {
  const ComponentType = AI_CHAT_COMPONENTS[component.type as keyof typeof AI_CHAT_COMPONENTS];
  
  if (!ComponentType) {
    console.warn(`Unknown component type: ${component.type}`);
    return null;
  }

  // Create action handlers based on component type
  const actionHandlers: any = {};
  
  if (component.type === 'todo-form') {
    actionHandlers.onSubmit = (data: any) => onAction(component.id, 'submit', data);
    actionHandlers.onCancel = () => onAction(component.id, 'cancel', null);
  } else if (component.type === 'name-change') {
    actionHandlers.onAccept = () => onAction(component.id, 'accept', null);
    actionHandlers.onCancel = () => onAction(component.id, 'cancel', null);
  } else if (component.type === 'confirmation') {
    actionHandlers.onConfirm = () => onAction(component.id, 'confirm', null);
    actionHandlers.onCancel = () => onAction(component.id, 'cancel', null);
  } else if (component.type === 'data-display') {
    actionHandlers.onAction = (action: string, data: any) => onAction(component.id, action, data);
  } else if (component.type === 'progress-tracker') {
    actionHandlers.onComplete = () => onAction(component.id, 'complete', null);
  } else if (component.type === 'quick-actions') {
    actionHandlers.onAction = (actionId: string) => onAction(component.id, 'click', actionId);
  } else if (component.type === 'alarm-form') {
    actionHandlers.onSubmit = (data: any) => onAction(component.id, 'submit', data);
    actionHandlers.onCancel = () => onAction(component.id, 'cancel', null);
  }

  return (
    <ComponentType
      key={component.id}
      {...component.props}
      {...actionHandlers}
    />
  );
}; 