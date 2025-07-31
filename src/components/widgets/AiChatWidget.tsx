import React, { useState, useRef, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { UIWidget } from '../../types';
import { socketService } from '../../services/socket';
import { renderAiChatComponent, AiChatComponent } from './ai-chat/AiChatComponents';
import { AIResponseGenerator, AIResponse } from '../../services/aiResponseGenerator';

interface Message {
  id: string;
  type: 'user' | 'ai' | 'thinking';
  content: string;
  timestamp: Date;
  thinkingSteps?: string[];
  components?: AiChatComponent[];
  isComplete?: boolean;
}

interface AiChatWidgetProps {
  widget: UIWidget;
  onRemove: () => void;
}

const AiChatWidget: React.FC<AiChatWidgetProps> = ({ widget, onRemove }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Hello! I\'m your AI assistant. I can help you with various tasks and provide real-time insights. What would you like to work on today?',
      timestamp: new Date(),
      isComplete: true
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Connect to socket service on mount
  useEffect(() => {
    const handleConnection = (data: any) => {
      setIsConnected(data.status === 'connected');
    };

    const handleThinking = (data: any) => {
      setMessages(prev => 
        prev.map(msg => 
          msg.type === 'thinking' 
            ? { ...msg, thinkingSteps: [...(msg.thinkingSteps || []), data.step] }
            : msg
        )
      );
    };

    const handleResponse = (data: any) => {
      const aiResponse: Message = {
        id: Date.now().toString(),
        type: 'ai',
        content: data.content,
        timestamp: new Date(),
        components: data.components,
        isComplete: true
      };

      setMessages(prev => 
        prev.map(msg => 
          msg.type === 'thinking' 
            ? { ...msg, isComplete: true }
            : msg
        ).concat(aiResponse)
      );
      setIsTyping(false);
    };

    const handleError = (data: any) => {
      console.error('Socket error:', data);
      setIsTyping(false);
    };

    // Subscribe to socket events
    socketService.on('connection', handleConnection);
    socketService.on('thinking', handleThinking);
    socketService.on('response', handleResponse);
    socketService.on('error', handleError);

    // Connect to socket
    socketService.connect().catch(console.error);

    // Cleanup on unmount
    return () => {
      socketService.off('connection', handleConnection);
      socketService.off('thinking', handleThinking);
      socketService.off('response', handleResponse);
      socketService.off('error', handleError);
    };
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
      isComplete: true
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Add thinking message
    const thinkingMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'thinking',
      content: 'Processing your request...',
      timestamp: new Date(),
      thinkingSteps: [],
      isComplete: false
    };

    setMessages(prev => [...prev, thinkingMessage]);

    // Send message via socket if connected, otherwise simulate
    if (isConnected) {
      socketService.sendChatMessage(inputValue.trim());
    } else {
      // Fallback simulation when socket is not connected
      const thinkingSteps = [
        'Analyzing your request...',
        'Gathering relevant information...',
        'Processing context and constraints...',
        'Generating response...',
        'Preparing interactive components...'
      ];

      for (let i = 0; i < thinkingSteps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 800));
        setMessages(prev => 
          prev.map(msg => 
            msg.id === thinkingMessage.id 
              ? { ...msg, thinkingSteps: thinkingSteps.slice(0, i + 1) }
              : msg
          )
        );
      }

      // Simulate AI response with interactive components
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Generate AI response using the response generator
      const aiResponseData = AIResponseGenerator.generateResponse(inputValue.trim());
      
      const aiResponse: Message = {
        id: (Date.now() + 2).toString(),
        type: 'ai',
        content: aiResponseData.response,
        timestamp: new Date(),
        components: aiResponseData.components,
        isComplete: true
      };

      setMessages(prev => 
        prev.map(msg => 
          msg.id === thinkingMessage.id 
            ? { ...msg, isComplete: true }
            : msg
        ).concat(aiResponse)
      );

      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInteractiveAction = async (componentId: string, action: string, data: any) => {
    console.log('Interactive action:', componentId, action, data);
    
    if (isConnected) {
      socketService.sendInteractiveAction(componentId, action, data);
    } else {
      // Generate follow-up response for offline mode
      const followUpResponse = AIResponseGenerator.generateFollowUpResponse(componentId, action, data);
      
      // Add thinking message
      const thinkingMessage: Message = {
        id: Date.now().toString(),
        type: 'thinking',
        content: 'Processing your action...',
        timestamp: new Date(),
        thinkingSteps: [],
        isComplete: false
      };

      setMessages(prev => [...prev, thinkingMessage]);

      // Simulate thinking steps
      for (let i = 0; i < followUpResponse.thinkingSteps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 600));
        setMessages(prev => 
          prev.map(msg => 
            msg.id === thinkingMessage.id 
              ? { ...msg, thinkingSteps: followUpResponse.thinkingSteps.slice(0, i + 1) }
              : msg
          )
        );
      }

      // Add AI response
      await new Promise(resolve => setTimeout(resolve, 300));
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: followUpResponse.response,
        timestamp: new Date(),
        components: followUpResponse.components,
        isComplete: true
      };

      setMessages(prev => 
        prev.map(msg => 
          msg.id === thinkingMessage.id 
            ? { ...msg, isComplete: true }
            : msg
        ).concat(aiResponse)
      );
    }
  };

  const renderMessage = (message: Message) => {
    switch (message.type) {
      case 'user':
        return (
          <div className="flex justify-end mb-4">
            <div className="max-w-[80%] bg-primary text-primary-foreground rounded-2xl rounded-br-md px-4 py-2 shadow-sm">
              <p className="text-sm">{message.content}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        );

      case 'ai':
        return (
          <div className="flex justify-start mb-4">
            <div className="max-w-[80%] bg-card border rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
              <div className="flex items-start gap-2 mb-2">
                <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  AI
                </div>
                <p className="text-sm">{message.content}</p>
              </div>
              
              {message.components && (
                <div className="mt-3 space-y-2">
                  {message.components.map(component => (
                    <div key={component.id}>
                      {renderAiChatComponent(component, handleInteractiveAction)}
                    </div>
                  ))}
                </div>
              )}
              
              <span className="text-xs text-muted-foreground mt-2 block">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        );

      case 'thinking':
        return (
          <div className="flex justify-start mb-4">
            <div className="max-w-[80%] bg-card border rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
              <div className="flex items-start gap-2 mb-3">
                <div className="w-6 h-6 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-full flex items-center justify-center text-white text-xs font-bold animate-pulse">
                  🤔
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground mb-2">
                    AI is thinking...
                  </p>
                  
                                     {message.thinkingSteps && (
                     <div className="space-y-1">
                       {message.thinkingSteps.map((step, index) => (
                         <div key={index} className="flex items-center gap-2 animate-in slide-in-from-left-2 duration-300" style={{ animationDelay: `${index * 100}ms` }}>
                           <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                           <span className="text-xs text-muted-foreground">{step}</span>
                         </div>
                       ))}
                     </div>
                   )}
                  
                                     {!message.isComplete && (
                     <div className="flex items-center gap-1 mt-2">
                       <div className="flex space-x-1">
                         <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce"></div>
                         <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                         <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                       </div>
                       <span className="text-xs text-muted-foreground ml-2">Processing...</span>
                     </div>
                   )}
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <BaseWidget
      title="AI Chat Assistant"
      icon="🤖"
      onRemove={onRemove}
      className="flex flex-col"
    >
      <div className="flex-1 flex flex-col h-full">
        {/* Header with connection status */}
        <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/30">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            } ${!isConnected && 'animate-pulse'}`}></div>
            <span className="text-xs text-muted-foreground">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
            {!isConnected && (
              <button
                onClick={() => socketService.connect()}
                className="text-xs text-primary hover:text-primary/80 underline"
              >
                Reconnect
              </button>
            )}
          </div>
          <div className="text-xs text-muted-foreground">
            Real-time AI
          </div>
        </div>

        {/* Messages container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {messages.map(renderMessage)}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t bg-muted/30 p-4">
          <div className="flex items-end gap-2">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything... (Shift+Enter for new line)"
                className="w-full resize-none border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                rows={1}
                style={{ minHeight: '40px', maxHeight: '120px' }}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isTyping ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                'Send'
              )}
            </button>
          </div>
          
          {/* Typing indicator */}
          {isTyping && (
            <div className="mt-2 text-xs text-muted-foreground">
              AI is responding...
            </div>
          )}
        </div>
      </div>
    </BaseWidget>
  );
};

export default AiChatWidget; 