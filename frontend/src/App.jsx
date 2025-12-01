import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Send, Menu, Inbox, Star, Clock, Send as SendIcon, File, ChevronDown, Search, MoreVertical } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'agent', content: 'Hello! I am your Digital Declutter Assistant. How can I help you triage your inbox today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('/chat', { message: input });
      setMessages(prev => [...prev, { role: 'agent', content: response.data.response }]);
    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, { role: 'agent', content: "**Error:** Failed to connect. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-white font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col flex-shrink-0">
        <div className="p-4">
          <button className="w-full bg-white hover:shadow-md text-gray-700 font-medium py-3 px-6 rounded-full shadow border border-gray-300 mb-6 transition-shadow">
            <span className="text-xl mr-2">✏️</span>
            Compose
          </button>
          <nav className="space-y-1">
            <NavItem icon={<Inbox size={20} />} label="Inbox" active count="10" />
            <NavItem icon={<Star size={20} />} label="Starred" />
            <NavItem icon={<Clock size={20} />} label="Snoozed" />
            <NavItem icon={<SendIcon size={20} />} label="Sent" />
            <NavItem icon={<File size={20} />} label="Drafts" count="2" />
            <NavItem icon={<ChevronDown size={20} />} label="More" />
          </nav>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-6 flex-shrink-0">
          <button className="p-2 hover:bg-gray-100 rounded-full mr-4 transition-colors">
            <Menu size={24} className="text-gray-600" />
          </button>
          <div className="flex-1 max-w-3xl bg-gray-100 rounded-lg px-4 py-2 flex items-center">
            <Search size={20} className="text-gray-500 mr-3" />
            <input type="text" placeholder="Search mail" className="bg-transparent border-none focus:outline-none w-full text-sm text-gray-700" />
          </div>
          <button className="p-2 hover:bg-gray-100 rounded-full ml-4 transition-colors">
            <MoreVertical size={20} className="text-gray-600" />
          </button>
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm ml-2">
            U
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-gray-50 p-6">
          <div className="max-w-5xl mx-auto space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-3xl px-5 py-3 ${msg.role === 'user'
                  ? 'bg-blue-100 rounded-2xl rounded-tr-sm'
                  : 'bg-white border border-gray-200 rounded-2xl rounded-tl-sm shadow-sm'
                  }`}>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className={`font-semibold text-xs ${msg.role === 'user' ? 'text-blue-800' : 'text-gray-700'}`}>
                      {msg.role === 'user' ? 'You' : 'Declutter Assistant'}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <div className="prose prose-sm max-w-none text-gray-800 leading-relaxed">
                    <ReactMarkdown
                      components={{
                        h3: ({ node, ...props }) => <h3 className="text-md font-bold text-gray-800 mt-6 mb-3 bg-blue-50 p-2 rounded-lg border-l-4 border-blue-500" {...props} />,
                        ul: ({ node, ...props }) => <ul className="space-y-3 mb-4" {...props} />,
                        li: ({ node, ...props }) => <li className="text-gray-700 bg-white p-3 rounded-md border border-gray-100 shadow-sm text-sm leading-relaxed" {...props} />,
                        blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-green-500 bg-green-50 p-4 rounded-r-lg my-4 text-gray-800 shadow-sm" {...props} />,
                        strong: ({ node, ...props }) => <span className="font-bold text-gray-900" {...props} />,
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm shadow-sm px-5 py-3 flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 bg-white p-4 flex-shrink-0">
          <div className="max-w-5xl mx-auto">
            <div className="relative bg-white border border-gray-300 rounded-3xl shadow-sm focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
                placeholder="Type a message..."
                className="w-full border-none rounded-3xl pl-5 pr-14 py-3 focus:outline-none resize-none text-sm"
                rows="1"
                style={{ minHeight: '44px', maxHeight: '120px' }}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="absolute right-2 bottom-2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <Send size={18} />
              </button>
            </div>
            <p className="text-center text-xs text-gray-400 mt-2">
              Declutter Assistant can make mistakes. Check important info.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active, count }) {
  return (
    <div className={`flex items-center justify-between px-4 py-2 rounded-r-full cursor-pointer transition-colors ${active ? 'bg-red-100 text-red-700 font-medium' : 'text-gray-700 hover:bg-gray-200'
      }`}>
      <div className="flex items-center space-x-3">
        <span className={active ? 'text-red-700' : 'text-gray-600'}>{icon}</span>
        <span className="text-sm">{label}</span>
      </div>
      {count && <span className={`text-xs font-semibold ${active ? 'text-red-700' : 'text-gray-600'}`}>{count}</span>}
    </div>
  );
}
