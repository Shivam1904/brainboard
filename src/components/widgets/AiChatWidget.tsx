import React, { useState, useRef, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { DailyWidget } from '../../services/api';
import { aiWebSocket } from '../../config/api';
import { formatTime, getTodayDateString } from '../../utils/dateUtils';

interface Message {
  id: string;
  type: string;
  content?: string;
  details?: string;
  timestamp: Date;
}

interface AiChatWidgetProps {
  widget: DailyWidget;
  onRemove: () => void;
}

// Track if we've already shown the welcome message this page load (avoids duplicate when React Strict Mode double-mounts)
let hasShownWelcomeThisSession = false;

const AiChatWidget: React.FC<AiChatWidgetProps> = ({ onRemove }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Connect to WebSocket on mount
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = aiWebSocket.connect(
        // onMessage handler
        (data: unknown) => {
          const messageData = data as Record<string, unknown>;
          // Handle connection status - don't add connection message to chat
          if (messageData.type === 'connection') {
            setIsConnected(true);
            // Show welcome message only once per page load (avoids duplicate on Strict Mode remount)
            if (!hasShownWelcomeThisSession) {
              hasShownWelcomeThisSession = true;
              const welcomeMessage: Message = {
                id: 'welcome-' + Date.now(),
                type: 'thinking',
                details: 'AI service ready! Send me a message to get started.',
                timestamp: new Date()
              };
              setMessages(prev => [...prev, welcomeMessage]);
            }
            return;
          }

          // Don't add the initial "thinking" welcome step - we already show one above
          if (messageData.type === 'thinking' && messageData.step === 'welcome') {
            return;
          }

          // Stop processing indicator for response or error
          if (messageData.type === 'response' || messageData.type === 'error') {
            setIsProcessing(false);
          }

          // For any socket ping that comes in, we will show it
          const content = messageData.content as Record<string, unknown> | undefined;
          const aiResponse = content?.ai_response as Record<string, unknown> | undefined;
          let messageContent = (content?.message as string) || (aiResponse?.ai_response as string);
          let messageType = (messageData.type as string) || 'unknown';

          // Handle malformed responses gracefully
          if (messageData.type === 'error' && messageContent?.includes('Failed to parse AI response')) {
            messageType = 'error';
            messageContent = 'The AI response could not be processed. Please try rephrasing your request.';
          }

          const message: Message = {
            id: Date.now().toString() + '-' + messageType + '-' + Math.random().toString(36).substring(2, 15),
            type: messageType,
            content: messageContent,
            details: messageData.details as string,
            timestamp: new Date()
          };

          setMessages(prev => [...prev, message]);
        },
        // onError handler
        (error: unknown) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
        },
        // onClose handler
        () => {
          setIsConnected(false);
        }
      );

      // Set connection status when WebSocket opens
      ws.onopen = () => {
        setIsConnected(true);
      };

      setWebsocket(ws);
    };

    connectWebSocket();

  }, []);


  const handleSendMessage = async () => {
    if (!inputValue.trim() || isProcessing || !isConnected) {
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsProcessing(true);

    try {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        // Just send the current message - backend will maintain conversation history
        aiWebSocket.sendMessage(
          websocket,
          inputValue.trim(),
          [], // user_tasks
          getTodayDateString(), // todays_date
          [] // No conversation history needed - backend maintains state
        );
      } else {
        throw new Error('WebSocket not connected');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setIsProcessing(false);

      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'error',
        content: 'Failed to send message. Please try again.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleReconnect = () => {
    if (websocket) {
      websocket.close();
    }
    setIsConnected(false);
    setWebsocket(null);
    // The useEffect will handle reconnection
  };



  const renderMessage = (message: Message) => {
    const getMessageStyle = () => {
      switch (message.type) {
        case 'user':
          return 'bg-blue-50 border-blue-200 p-2 ml-8';
        case 'response':
          return 'bg-green-50 border-green-200 p-2 mr-8';
        case 'thinking':
          return 'mr-8 max-w-xs';
        case 'error':
          return 'bg-red-50 border-red-200';
        default:
          return '';
      }
    };

    const getMessageIcon = () => {
      switch (message.type) {
        case 'user':
          return '👤';
        case 'response':
          return '🤖';
        case 'thinking':
          return '💭';
        case 'error':
          return '⚠️';
        default:
          return '💬';
      }
    };

    const getMessageTitle = () => {
      switch (message.type) {
        case 'user':
          return 'You';
        case 'response':
          return 'AI Assistant';
        case 'thinking':
          return 'AI Thinking';
        case 'error':
          return 'Error';
        default:
          return message.type.charAt(0).toUpperCase() + message.type.slice(1);
      }
    };

    return (
      <div key={message.id} className={`${getMessageStyle()} rounded-lg shadow-sm`}>
        {/* Message Header */}
        {(message.type === 'response' || message.type === 'user') && (<div className={`flex items-center gap-3 border-b border-gray-100`}>
          <span className={`text-lg`}>{getMessageIcon()}</span>
          <div className="flex-1">
            <span className={`font-semibold text-gray-700 text-xs`}>
              {getMessageTitle()}
            </span>
            <span className={`text-gray-500 ml-2 text-xs`}>
              {formatTime(message.timestamp, {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </div>
        </div>)}

        {/* Message Content */}
        <div>
          {/* Show content->message field for response type */}
          {(message.type === 'response' || message.type === 'user') && message.content && (
            <div className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
              {message.content + ''}
            </div>
          )}

          {/* Show details field for thinking type */}
          {message.type === 'thinking' && message.details && (
            <div className="text-xs text-yellow-800 italic leading-tight">
              {message.details + ''}
            </div>
          )}

          {/* Show content for other types */}
          {message.type !== 'response' && message.type !== 'thinking' && message.type !== 'user' && (
            <div className={`flex items-center `}>
              <div className="flex flex-row flex-1 justify-between">
                <span className={`font-semibold text-gray-700 text-xs`}>
                  {getMessageTitle()}
                </span>
                <span className={`text-gray-500 text-xs`}>
                  {formatTime(message.timestamp, {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <BaseWidget
      title="AI Chat"
      icon="🤖"
      onRemove={onRemove}
    >
      <div className="flex-1 flex flex-col min-h-[300px] h-full">
        {/* Header with connection status */}
        <div className="flex items-center justify-between px-4 border-b bg-muted/30">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
            <span className="text-xs text-muted-foreground">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
            {!isConnected && (
              <button
                onClick={handleReconnect}
                className="text-xs text-primary hover:text-primary/80 underline"
              >
                Reconnect
              </button>
            )}
          </div>
        </div>

        {/* Messages container */}
        <div className="flex-1 overflow-y-auto pt-1">
          {messages.map((message) => renderMessage(message))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t bg-muted/30">
          <div className="flex items-end gap-1">
            <div className="flex-1 relative ">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => handleKeyPress(e)}
                onFocus={() => {
                  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
                }}
                placeholder="Ask me anything... (Shift+Enter for new line)"
                className="w-full resize-none  px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                rows={2}
                disabled={!isConnected}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isProcessing || !isConnected}
              className="px-2 py-1  bg-primary text-primary-foreground rounded-lg text-xs font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isProcessing ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                'Send'
              )}
            </button>
          </div>

          {/* Processing indicator */}
          {isProcessing && (
            <div className="mt-2 text-xs text-muted-foreground">
              AI is processing...
            </div>
          )}

          {/* Connection status */}
          {!isConnected && (
            <div className="mt-2 text-xs text-red-500">
              Not connected to AI service. Please reconnect.
            </div>
          )}
        </div>
      </div>
    </BaseWidget>
  );
};

export default AiChatWidget;
