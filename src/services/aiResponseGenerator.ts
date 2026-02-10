import { RESPONSE_PATTERNS, DEFAULT_RESPONSE, AIResponse } from '../config/aiPatterns';
import { formatDateTime, getCurrentTimeInZone } from '../utils/dateUtils';

// Re-export AIResponse interface for compatibility
export type { AIResponse };

export class AIResponseGenerator {
  private static findMatchingPattern(userInput: string): string | null {
    const input = userInput.toLowerCase().trim();

    for (const [patternKey, pattern] of Object.entries(RESPONSE_PATTERNS)) {
      for (const trigger of pattern.triggers) {
        if (input.includes(trigger.toLowerCase())) {
          return patternKey;
        }
      }
    }

    return null;
  }

  static generateResponse(userInput: string): AIResponse {
    const patternKey = this.findMatchingPattern(userInput);

    if (patternKey && RESPONSE_PATTERNS[patternKey as keyof typeof RESPONSE_PATTERNS]) {
      return RESPONSE_PATTERNS[patternKey as keyof typeof RESPONSE_PATTERNS];
    }

    return DEFAULT_RESPONSE;
  }

  static generateFollowUpResponse(componentId: string, action: string, data: unknown): AIResponse {
    // Handle follow-up responses based on component actions
    switch (componentId) {
      case 'todo-form-1':
        if (action === 'submit') {
          const todoData = data as Record<string, unknown>;
          return {
            thinkingSteps: [
              'Processing todo submission...',
              'Validating todo data...',
              'Creating todo item...',
              'Saving to database...'
            ],
            response: `Great! I've created a new todo: "${todoData.title}". ${todoData.description ? `Description: ${todoData.description}` : ''}`,
            components: [
              {
                id: 'todo-success',
                type: 'data-display',
                props: {
                  title: 'Todo Created Successfully',
                  data: {
                    title: todoData.title,
                    description: todoData.description || 'No description',
                    status: 'Pending',
                    created: formatDateTime(getCurrentTimeInZone())
                  }
                }
              }
            ]
          };
        }
        break;

      case 'name-change-1':
        if (action === 'accept') {
          return {
            thinkingSteps: [
              'Processing name change request...',
              'Preparing name input form...',
              'Setting up validation...'
            ],
            response: 'Please enter your new name:',
            components: [
              {
                id: 'name-input',
                type: 'todo-form',
                props: {
                  title: 'New Name',
                  description: 'Enter your new name'
                }
              }
            ]
          };
        }
        break;

      case 'confirm-1':
        if (action === 'confirm') {
          return {
            thinkingSteps: [
              'Processing confirmation...',
              'Executing requested action...',
              'Updating system...'
            ],
            response: 'Action confirmed and completed successfully!',
            components: []
          };
        }
        break;

      case 'quick-1':
        if (action === 'click') {
          const actionMap: Record<string, AIResponse> = {
            'create-todo': {
              thinkingSteps: [
                'Opening todo creation...',
                'Preparing todo form...'
              ],
              response: 'Let\'s create a new todo item:',
              components: [
                {
                  id: 'todo-form-quick',
                  type: 'todo-form',
                  props: {}
                }
              ]
            },
            'set-alarm': {
              thinkingSteps: [
                'Opening alarm creation...',
                'Preparing alarm form...'
              ],
              response: 'Let\'s set up a new alarm:',
              components: [
                {
                  id: 'alarm-form',
                  type: 'data-display',
                  props: {
                    title: 'Alarm Setup',
                    data: 'Alarm creation form will be implemented here'
                  }
                }
              ]
            },
            'track-item': {
              thinkingSteps: [
                'Opening item tracker...',
                'Preparing tracking interface...'
              ],
              response: 'Let\'s set up item tracking:',
              components: [
                {
                  id: 'tracker-form',
                  type: 'data-display',
                  props: {
                    title: 'Item Tracker',
                    data: 'Item tracking form will be implemented here'
                  }
                }
              ]
            },
            'web-search': {
              thinkingSteps: [
                'Opening web search...',
                'Preparing search interface...'
              ],
              response: 'Let\'s search the web:',
              components: [
                {
                  id: 'search-form',
                  type: 'data-display',
                  props: {
                    title: 'Web Search',
                    data: 'Web search form will be implemented here'
                  }
                }
              ]
            }
          };

          return actionMap[data as string] || DEFAULT_RESPONSE;
        }
        break;
    }

    return DEFAULT_RESPONSE;
  }
}