import { useState } from 'react';
import type { GenerateResponse } from './types/api';
import { generateResponse, calculateApiCost } from './utils/api';
import PromptInput from './components/PromptInput';
import ResponseDisplay from './components/ResponseDisplay';
import RoutingExplanation from './components/RoutingExplanation';
import CostPanel from './components/CostPanel';
import DecisionFlow from './components/DecisionFlow';
import WhyNotOtherTiers from './components/WhyNotOtherTiers';

function App() {
  const [prompt, setPrompt] = useState('');
  const [context, setContext] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [latency, setLatency] = useState<number>(0);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    const startTime = performance.now();

    try {
      const response = await generateResponse({
        prompt,
        context,
        constraints: {
          max_latency_ms: 2000,
          max_cost_usd: 0.01,
          risk_level: 'low',
        },
        debug: true,
      });

      const endTime = performance.now();
      setLatency((endTime - startTime) / 1000);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const apiOnlyCost = result ? calculateApiCost(result.tokens_used) : 0;
  const costSaved = result ? ((apiOnlyCost - result.estimated_cost_usd) / apiOnlyCost) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">LLM Router</h1>
              <p className="text-sm text-slate-600">Intelligent model selection for cost optimization</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Input Section */}
        <div className="mb-8">
          <PromptInput
            prompt={prompt}
            context={context}
            onPromptChange={setPrompt}
            onContextChange={setContext}
            onGenerate={handleGenerate}
            loading={loading}
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Top Metrics Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <CostPanel
                actualCost={result.estimated_cost_usd}
                apiCost={apiOnlyCost}
                costSaved={costSaved}
                cacheHit={result.cache_hit}
              />
              
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-700">Latency</h3>
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    latency < 1 ? 'bg-green-100 text-green-700' :
                    latency < 3 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {latency < 1 ? 'Fast' : latency < 3 ? 'Medium' : 'Slow'}
                  </div>
                </div>
                <div className="text-3xl font-bold text-slate-900">{latency.toFixed(2)}s</div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-sm font-semibold text-slate-700 mb-4">Tokens</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Input</span>
                    <span className="font-medium text-slate-900">{result.tokens_used.input}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">Output</span>
                    <span className="font-medium text-slate-900">{result.tokens_used.output}</span>
                  </div>
                  <div className="pt-2 border-t border-slate-200 flex justify-between text-sm font-semibold">
                    <span className="text-slate-700">Total</span>
                    <span className="text-slate-900">{result.tokens_used.input + result.tokens_used.output}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Decision Flow */}
            {result.debug && (
              <DecisionFlow debug={result.debug} finalModel={result.model_used} />
            )}

            {/* Why Not Other Tiers */}
            {result.debug && (
              <WhyNotOtherTiers debug={result.debug} modelUsed={result.model_used} />
            )}

            {/* Routing Explanation */}
            {result.debug && (
              <RoutingExplanation debug={result.debug} modelUsed={result.model_used} />
            )}

            {/* Response Display */}
            <ResponseDisplay response={result.response} modelUsed={result.model_used} />
          </div>
        )}

        {/* Empty State */}
        {!result && !loading && !error && (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 mb-4">
              <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Enter a prompt to see routing in action</h3>
            <p className="text-slate-600 max-w-md mx-auto">
              The system will intelligently route your request to the most cost-effective model while maintaining quality.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;