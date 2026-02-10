import React from 'react';
import {
    AiChatComponent,
    TodoFormComponent,
    NameChangeComponent,
    ConfirmationComponent,
    DataDisplayComponent,
    ProgressTrackerComponent,
    QuickActionsComponent,
    AlarmFormComponent
} from './AiChatComponents';

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
    onAction: (componentId: string, action: string, data: unknown) => void
) => {
    const ComponentType = AI_CHAT_COMPONENTS[component.type as keyof typeof AI_CHAT_COMPONENTS];

    if (!ComponentType) {
        console.warn(`Unknown component type: ${component.type}`);
        return null;
    }

    // Create action handlers based on component type
    const actionHandlers: Record<string, unknown> = {};

    if (component.type === 'todo-form') {
        actionHandlers.onSubmit = (data: unknown) => onAction(component.id, 'submit', data);
        actionHandlers.onCancel = () => onAction(component.id, 'cancel', null);
    } else if (component.type === 'name-change') {
        actionHandlers.onAccept = () => onAction(component.id, 'accept', null);
        actionHandlers.onCancel = () => onAction(component.id, 'cancel', null);
    } else if (component.type === 'confirmation') {
        actionHandlers.onConfirm = () => onAction(component.id, 'confirm', null);
        actionHandlers.onCancel = () => onAction(component.id, 'cancel', null);
    } else if (component.type === 'data-display') {
        actionHandlers.onAction = (action: string, data: unknown) => onAction(component.id, action, data);
    } else if (component.type === 'progress-tracker') {
        actionHandlers.onComplete = () => onAction(component.id, 'complete', null);
    } else if (component.type === 'quick-actions') {
        actionHandlers.onAction = (actionId: string) => onAction(component.id, 'click', actionId);
    } else if (component.type === 'alarm-form') {
        actionHandlers.onSubmit = (data: unknown) => onAction(component.id, 'submit', data);
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
