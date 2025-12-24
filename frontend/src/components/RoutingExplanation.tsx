import type { DebugInfo, ModelTier } from '../types/api';
import ModelBadge from './ModelBadge';

interface RoutingExplanationProps {
  debug: DebugInfo;
  modelUsed: ModelTier;
}

export default function RoutingExplanation({ debug, modelUsed }: RoutingExplanationProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-900">Routing Explanation</h3>
        <ModelBadge model={modelUsed} />
      </div>

      <div className="space-y-6">
        {/* Static Rule */}
        {debug.static_rule && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-semibold text-blue-900">Static Rule Applied</span>
            </div>
            <p className="text-sm text-blue-800 mb-2">
              <span className="font-medium">{debug.static_rule.rule_name}</span>
            </p>
            <div className="text-xs text-blue-700 font-mono bg-blue-100 rounded p-2">
              {JSON.stringify(debug.static_rule.matched_condition, null, 2)}
            </div>
          </div>
        )}

        {/* Classifier */}
        {debug.classifier && (
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <span className="font-semibold text-purple-900">ML Classifier Prediction</span>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-purple-700">Predicted Task</span>
                <span className="px-2 py-1 bg-purple-100 text-purple-900 rounded text-sm font-medium">
                  {debug.classifier.predicted_task}
                </span>
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-purple-700">Confidence</span>
                  <span className="text-sm font-semibold text-purple-900">
                    {(debug.classifier.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                
                {/* Enhanced confidence bar with threshold markers */}
                <div className="relative">
                  <div className="w-full h-3 bg-purple-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        debug.classifier.confidence >= 0.7 ? 'bg-green-500' :
                        debug.classifier.confidence >= 0.45 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${debug.classifier.confidence * 100}%` }}
                    />
                  </div>
                  
                  {/* Threshold markers */}
                  <div className="absolute top-0 w-full h-3 pointer-events-none">
                    {/* 45% threshold */}
                    <div className="absolute left-[45%] top-0 h-full w-0.5 bg-purple-400" />
                    {/* 70% threshold */}
                    <div className="absolute left-[70%] top-0 h-full w-0.5 bg-purple-400" />
                  </div>
                </div>
                
                <div className="flex justify-between text-xs mt-2">
                  <span className={`font-medium ${debug.classifier.confidence < 0.45 ? 'text-red-600' : 'text-slate-500'}`}>
                    Low (0-45%)
                  </span>
                  <span className={`font-medium ${debug.classifier.confidence >= 0.45 && debug.classifier.confidence < 0.7 ? 'text-yellow-600' : 'text-slate-500'}`}>
                    Medium (45-70%)
                  </span>
                  <span className={`font-medium ${debug.classifier.confidence >= 0.7 ? 'text-green-600' : 'text-slate-500'}`}>
                    High (70-100%)
                  </span>
                </div>
                
                {/* Routing decision based on confidence */}
                <div className="mt-3 p-2 bg-purple-100 rounded text-xs">
                  <span className="font-semibold text-purple-900">Routing Logic: </span>
                  <span className="text-purple-800">
                    {debug.classifier.confidence >= 0.7 
                      ? 'High confidence → Trust classifier prediction'
                      : debug.classifier.confidence >= 0.45
                      ? 'Medium confidence → Route to medium tier for safety'
                      : 'Low confidence → Escalate to API for quality'}
                  </span>
                </div>
              </div>

              {debug.classifier.confidence_band && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-purple-700">Confidence Band:</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    debug.classifier.confidence_band === 'high_uncertainty' ? 'bg-green-100 text-green-700' :
                    debug.classifier.confidence_band === 'medium_uncertainty' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {debug.classifier.confidence_band}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Heuristics */}
        {debug.heuristics && (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span className="font-semibold text-amber-900">Heuristic Analysis</span>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-amber-700 block mb-1">Context Ratio</span>
                <span className="text-lg font-bold text-amber-900">
                  {(debug.heuristics.context_ratio * 100).toFixed(0)}%
                </span>
              </div>
              <div>
                <span className="text-xs text-amber-700 block mb-1">Generation Weight</span>
                <span className="text-lg font-bold text-amber-900 capitalize">
                  {debug.heuristics.generation_weight}
                </span>
              </div>
            </div>

            {debug.heuristics.override && (
              <div className="mt-3 pt-3 border-t border-amber-200">
                <p className="text-sm text-amber-800">
                  <span className="font-semibold">Override Applied: </span>
                  {debug.heuristics.override.replace(/_/g, ' ')}
                </p>
              </div>
            )}

            {debug.heuristics.estimated_output_tokens && (
              <div className="mt-3 text-sm text-amber-700">
                Estimated output: <span className="font-semibold">{debug.heuristics.estimated_output_tokens}</span> tokens
              </div>
            )}
          </div>
        )}

        {/* Context Window Safety */}
        {debug.context_window && (
          <div className={`p-4 rounded-lg border ${
            debug.context_window.overflow
              ? 'bg-orange-50 border-orange-200'
              : 'bg-green-50 border-green-200'
          }`}>
            <div className="flex items-center gap-2 mb-3">
              <svg className={`w-5 h-5 ${debug.context_window.overflow ? 'text-orange-600' : 'text-green-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span className={`font-semibold ${debug.context_window.overflow ? 'text-orange-900' : 'text-green-900'}`}>
                Context Window Check
              </span>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className={debug.context_window.overflow ? 'text-orange-700' : 'text-green-700'}>
                  Total Tokens
                </span>
                <span className={`font-semibold ${debug.context_window.overflow ? 'text-orange-900' : 'text-green-900'}`}>
                  {debug.context_window.total_tokens}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className={debug.context_window.overflow ? 'text-orange-700' : 'text-green-700'}>
                  Max Allowed
                </span>
                <span className={`font-semibold ${debug.context_window.overflow ? 'text-orange-900' : 'text-green-900'}`}>
                  {debug.context_window.max_allowed}
                </span>
              </div>

              {debug.context_window.overflow && debug.context_window.escalated_from && (
                <div className={`mt-3 pt-3 border-t border-orange-200 text-sm text-orange-800`}>
                  <span className="font-semibold">⚠️ Escalated:</span> {debug.context_window.escalated_from} → {modelUsed}
                </div>
              )}

              {debug.context_window.warning && (
                <div className="mt-3 pt-3 border-t border-orange-200 text-sm text-orange-800 font-semibold">
                  ⚠️ {debug.context_window.warning.replace(/_/g, ' ')}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}