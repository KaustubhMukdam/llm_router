import { useState } from 'react';

interface PromptInputProps {
  prompt: string;
  context: string[];
  onPromptChange: (value: string) => void;
  onContextChange: (value: string[]) => void;
  onGenerate: () => void;
  loading: boolean;
}

export default function PromptInput({
  prompt,
  context,
  onPromptChange,
  onContextChange,
  onGenerate,
  loading,
}: PromptInputProps) {
  const [contextText, setContextText] = useState('');
  const [showContext, setShowContext] = useState(false);

  const handleAddContext = () => {
    if (contextText.trim()) {
      onContextChange([...context, contextText.trim()]);
      setContextText('');
    }
  };

  const handleRemoveContext = (index: number) => {
    onContextChange(context.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="space-y-4">
        {/* Prompt Input */}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Prompt
          </label>
          <textarea
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            placeholder="Enter your prompt here... (e.g., 'Explain how JWT authentication works')"
            className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-colors resize-none"
            rows={4}
            disabled={loading}
          />
        </div>

        {/* Context Toggle */}
        <button
          onClick={() => setShowContext(!showContext)}
          className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 transition-colors"
        >
          <svg
            className={`w-4 h-4 transition-transform ${showContext ? 'rotate-90' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span className="font-medium">Add context</span>
          {context.length > 0 && (
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">
              {context.length}
            </span>
          )}
        </button>

        {/* Context Input */}
        {showContext && (
          <div className="space-y-3 pl-6 border-l-2 border-slate-200">
            <div className="flex gap-2">
              <textarea
                value={contextText}
                onChange={(e) => setContextText(e.target.value)}
                placeholder="Add additional context..."
                className="flex-1 px-3 py-2 text-sm rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-colors resize-none"
                rows={2}
                disabled={loading}
              />
              <button
                onClick={handleAddContext}
                disabled={!contextText.trim() || loading}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 disabled:bg-slate-50 disabled:text-slate-400 text-slate-700 rounded-lg text-sm font-medium transition-colors"
              >
                Add
              </button>
            </div>

            {/* Context List */}
            {context.length > 0 && (
              <div className="space-y-2">
                {context.map((ctx, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-2 p-3 bg-slate-50 rounded-lg border border-slate-200"
                  >
                    <p className="flex-1 text-sm text-slate-700 line-clamp-2">{ctx}</p>
                    <button
                      onClick={() => handleRemoveContext(index)}
                      className="text-slate-400 hover:text-red-600 transition-colors"
                      disabled={loading}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Generate Button */}
        <button
          onClick={onGenerate}
          disabled={!prompt.trim() || loading}
          className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-slate-300 disabled:to-slate-300 text-white font-semibold rounded-lg transition-all shadow-lg shadow-blue-500/25 disabled:shadow-none flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Generating...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generate Response
            </>
          )}
        </button>
      </div>
    </div>
  );
}