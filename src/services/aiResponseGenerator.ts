import { AiChatComponent } from '../components/widgets/ai-chat/AiChatComponents';

// Response patterns for different user inputs
const RESPONSE_PATTERNS = {
  // Greeting patterns
  greeting: {
    triggers: ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening'],
    thinkingSteps: [
      'Recognizing greeting...',
      'Analyzing user intent...',
      'Preparing friendly response...'
    ],
    response: 'Hello! 👋 I\'m your AI assistant. I can help you with various tasks like creating todos, managing alarms, tracking items, and much more. What would you like to work on today?',
    components: []
  },

  // Todo patterns
  todo: {
    triggers: ['todo', 'task', 'create todo', 'add todo', 'new todo', 'reminder'],
    thinkingSteps: [
      'Detecting todo request...',
      'Analyzing todo requirements...',
      'Preparing todo form...',
      'Setting up form validation...'
    ],
    response: 'I\'ll help you create a new todo item. Please fill out the form below:',
    components: [
      {
        id: 'todo-form-1',
        type: 'todo-form',
        props: {}
      }
    ]
  },

  // Name change patterns
  nameChange: {
    triggers: ['change name', 'update name', 'rename', 'my name', 'name change'],
    thinkingSteps: [
      'Detecting name change request...',
      'Checking current user data...',
      'Preparing name change interface...'
    ],
    response: 'I can help you change your name. Here\'s the current information:',
    components: [
      {
        id: 'name-change-1',
        type: 'name-change',
        props: {
          currentName: 'John Doe'
        }
      }
    ]
  },

  // Progress tracking patterns
  progress: {
    triggers: ['progress', 'track', 'status', 'how much', 'percentage'],
    thinkingSteps: [
      'Analyzing progress request...',
      'Calculating current progress...',
      'Preparing progress tracker...'
    ],
    response: 'Here\'s your current progress on various tasks:',
    components: [
      {
        id: 'progress-1',
        type: 'progress-tracker',
        props: {
          current: 7,
          total: 10,
          label: 'Daily Tasks'
        }
      },
      {
        id: 'progress-2',
        type: 'progress-tracker',
        props: {
          current: 3,
          total: 5,
          label: 'Weekly Goals'
        }
      }
    ]
  },

  // Data display patterns
  data: {
    triggers: ['show data', 'my data', 'statistics', 'stats', 'information', 'details'],
    thinkingSteps: [
      'Gathering user data...',
      'Analyzing statistics...',
      'Preparing data display...'
    ],
    response: 'Here\'s your current data and statistics:',
    components: [
      {
        id: 'data-1',
        type: 'data-display',
        props: {
          title: 'User Statistics',
          data: {
            totalTodos: 15,
            completedTodos: 12,
            activeAlarms: 3,
            trackers: 2,
            lastActive: '2 hours ago'
          }
        }
      }
    ]
  },

  // Quick actions patterns
  quickActions: {
    triggers: ['quick', 'actions', 'menu', 'options', 'what can you do'],
    thinkingSteps: [
      'Analyzing available actions...',
      'Preparing quick action menu...',
      'Organizing common tasks...'
    ],
    response: 'Here are some quick actions you can take:',
    components: [
      {
        id: 'quick-1',
        type: 'quick-actions',
        props: {
          actions: [
            { id: 'create-todo', label: 'Create Todo', icon: '📝', action: 'create_todo' },
            { id: 'set-alarm', label: 'Set Alarm', icon: '⏰', action: 'set_alarm' },
            { id: 'track-item', label: 'Track Item', icon: '📊', action: 'track_item' },
            { id: 'search-web', label: 'Web Search', icon: '🔍', action: 'web_search' }
          ]
        }
      }
    ]
  },

  // Confirmation patterns
  confirm: {
    triggers: ['delete', 'remove', 'clear', 'reset', 'confirm'],
    thinkingSteps: [
      'Detecting confirmation request...',
      'Preparing confirmation dialog...',
      'Setting up safety checks...'
    ],
    response: 'I want to make sure you really want to do this. Please confirm:',
    components: [
      {
        id: 'confirm-1',
        type: 'confirmation',
        props: {
          message: 'Are you sure you want to proceed with this action? This cannot be undone.'
        }
      }
    ]
  },

  // Help patterns
  help: {
    triggers: ['help', 'what can you do', 'how to', 'guide', 'tutorial'],
    thinkingSteps: [
      'Analyzing help request...',
      'Preparing comprehensive guide...',
      'Organizing available features...'
    ],
    response: 'I\'m here to help! Here\'s what I can do for you:',
    components: [
      {
        id: 'help-1',
        type: 'data-display',
        props: {
          title: 'Available Features',
          data: {
            '📝 Todo Management': 'Create, edit, and track todos',
            '⏰ Alarm System': 'Set and manage alarms',
            '📊 Item Tracking': 'Track single items like weight, water intake',
            '🔍 Web Search': 'AI-powered web search and summaries',
            '📅 Calendar': 'View and manage calendar events',
            '⚙️ Settings': 'Manage your dashboard configuration'
          }
        }
      }
    ]
  }
};

// Default response for unrecognized inputs
const DEFAULT_RESPONSE = {
  thinkingSteps: [
    'Analyzing your request...',
    'Processing input...',
    'Generating helpful response...'
  ],
  response: 'I understand you\'re asking about something. Could you please be more specific? I can help you with todos, alarms, tracking, web searches, and more.',
  components: [
    {
      id: 'default-help',
      type: 'quick-actions',
      props: {
        actions: [
          { id: 'help', label: 'Get Help', icon: '❓', action: 'help' },
          { id: 'examples', label: 'See Examples', icon: '💡', action: 'examples' }
        ]
      }
    }
  ]
};

export interface AIResponse {
  thinkingSteps: string[];
  response: string;
  components: AiChatComponent[];
}

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

  static generateFollowUpResponse(componentId: string, action: string, data: any): AIResponse {
    // Handle follow-up responses based on component actions
    switch (componentId) {
      case 'todo-form-1':
        if (action === 'submit') {
          return {
            thinkingSteps: [
              'Processing todo submission...',
              'Validating todo data...',
              'Creating todo item...',
              'Saving to database...'
            ],
            response: `Great! I've created a new todo: "${data.title}". ${data.description ? `Description: ${data.description}` : ''}`,
            components: [
              {
                id: 'todo-success',
                type: 'data-display',
                props: {
                  title: 'Todo Created Successfully',
                  data: {
                    title: data.title,
                    description: data.description || 'No description',
                    status: 'Pending',
                    created: new Date().toLocaleString()
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
          
          return actionMap[data] || DEFAULT_RESPONSE;
        }
        break;
    }

    return DEFAULT_RESPONSE;
  }
} 