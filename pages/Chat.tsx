import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { Mic, MicOff, Volume2, VolumeX, RotateCcw } from "lucide-react";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useTextToSpeech } from "../hooks/useTextToSpeech";
import { useUser, UserButton } from "@clerk/clerk-react";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
}

export default function Chat() {
  const { user } = useUser();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: `Hello${user ? ` ${user.firstName}` : ''}! I'm TracWise, your AI assistant for tractor operations. Ask me anything about maintenance, troubleshooting, or operation procedures.`,
      sender: "ai",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // Load conversation history from localStorage on component mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('tracwise-chat-history');
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        // Validate the structure and add welcome message if none exists
        if (Array.isArray(parsedMessages) && parsedMessages.length > 0) {
          setMessages(parsedMessages.map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          })));
        }
      } catch (error) {
        console.error('Error loading chat history:', error);
        // Keep default welcome message
      }
    }
  }, [user]);

  // Save conversation history to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 1) { // Don't save just the welcome message
      localStorage.setItem('tracwise-chat-history', JSON.stringify(messages));
    }
  }, [messages]);
  const {
    transcript,
    isListening,
    startListening,
    stopListening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  const {
    isSpeaking,
    speak,
    stop: stopSpeaking,
    browserSupportsTextToSpeech,
  } = useTextToSpeech();

  const [currentSpeakingId, setCurrentSpeakingId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update input value when transcript changes
  useEffect(() => {
    if (transcript) {
      setInputValue(transcript);
    }
  }, [transcript]);

  const handleVoiceToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      startListening();
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Prepare conversation history for the API (excluding welcome message and current message)
      const conversationHistory = messages
        .filter(msg => msg.id !== "1") // Exclude welcome message
        .map(msg => ({
          text: msg.text,
          sender: msg.sender,
          timestamp: msg.timestamp
        }));

      const response = await fetch("https://tracwise-backend.onrender.com/api/qa/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: userMessage.text, 
          model: "General",
          conversation_history: conversationHistory
        }),
      });
      const data = await response.json();
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.answer,
        sender: "ai",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          text: "Sorry, there was an error connecting to the backend.",
          sender: "ai",
          timestamp: new Date(),
        },
      ]);
    }
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSpeak = (messageId: string, text: string) => {
    if (currentSpeakingId === messageId && isSpeaking) {
      // If currently speaking this message, stop it
      stopSpeaking();
      setCurrentSpeakingId(null);
    } else {
      // Start speaking this message
      setCurrentSpeakingId(messageId);
      speak(text);
    }
  };

  // Stop speaking when component unmounts or speech ends
  useEffect(() => {
    if (!isSpeaking) {
      setCurrentSpeakingId(null);
    }
  }, [isSpeaking]);

  const clearChatHistory = () => {
    const welcomeMessage = {
      id: "1",
      text: `Hello${user ? ` ${user.firstName}` : ''}! I'm TracWise, your AI assistant for tractor operations. Ask me anything about maintenance, troubleshooting, or operation procedures.`,
      sender: "ai" as const,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
    localStorage.removeItem('tracwise-chat-history');
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Chat Header */}
      <div className="border-b border-border p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              to="/"
              className="flex items-center text-primary hover:text-primary-glow transition-colors"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Back to Home
            </Link>
            <div>
              <h1 className="text-2xl font-semibold text-foreground">
                TracWise AI
              </h1>
              <p className="text-sm text-muted-foreground">
                Ask questions about tractor operations and maintenance
                {messages.length > 1 && (
                  <span className="text-green-600 ml-2">
                    • Context maintained ({messages.length - 1} message{messages.length !== 2 ? 's' : ''})
                  </span>
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
            <span className="text-sm text-muted-foreground">AI Online</span>
            {messages.length > 1 && (
              <Button
                variant="outline"
                size="sm"
                onClick={clearChatHistory}
                className="ml-4 text-gray-600 hover:text-gray-800"
                title="Clear chat history"
              >
                <RotateCcw size={16} className="mr-1" />
                Clear Chat
              </Button>
            )}
            <div className="ml-4">
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 relative ${
                  message.sender === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-card-foreground border border-border"
                }`}
              >
                <div className="text-sm leading-relaxed">
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </div>
                
                <div className="flex items-center justify-between mt-2">
                  <p className="text-xs opacity-70">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                  
                  {/* Speaker button for AI messages */}
                  {message.sender === "ai" && browserSupportsTextToSpeech && (
                    <button
                      onClick={() => handleSpeak(message.id, message.text)}
                      className={`ml-2 p-1 rounded transition-colors ${
                        currentSpeakingId === message.id && isSpeaking
                          ? "text-blue-600 hover:text-blue-700"
                          : "text-gray-500 hover:text-gray-700"
                      }`}
                      title={
                        currentSpeakingId === message.id && isSpeaking
                          ? "Stop speaking"
                          : "Listen to response"
                      }
                    >
                      {currentSpeakingId === message.id && isSpeaking ? (
                        <VolumeX size={16} />
                      ) : (
                        <Volume2 size={16} />
                      )}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-card text-card-foreground border border-border rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-primary rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-primary rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    TracWise is thinking...
                  </span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input Section */}
      <div className="border-t bg-white p-4">
        <div className="flex items-center space-x-2 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder={
                isListening
                  ? "Listening..."
                  : "Ask about your tractor..."
              }
              className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${
                isListening ? "border-red-500 bg-red-50" : "border-gray-300"
              }`}
              disabled={isLoading}
            />
            {isListening && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              </div>
            )}
          </div>

          {/* Voice Input Button */}
          {browserSupportsSpeechRecognition && (
            <button
              onClick={handleVoiceToggle}
              className={`p-3 rounded-lg border transition-colors ${
                isListening
                  ? "bg-red-500 text-white border-red-500 hover:bg-red-600"
                  : "bg-white text-gray-600 border-gray-300 hover:bg-gray-50"
              }`}
              title={isListening ? "Stop recording" : "Start voice input"}
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
          )}

          {/* Send Button */}
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>

        {/* Voice status indicator */}
        {isListening && (
          <div className="text-center mt-2">
            <p className="text-sm text-red-600">
              🎤 Listening... Click the mic button to stop
            </p>
          </div>
        )}
      </div>
    </div>
  );
}