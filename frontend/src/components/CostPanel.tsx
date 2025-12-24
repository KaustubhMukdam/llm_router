interface CostPanelProps {
  actualCost: number;
  apiCost: number;
  costSaved: number;
  cacheHit: boolean;
}

export default function CostPanel({ actualCost, apiCost, costSaved, cacheHit }: CostPanelProps) {
  const savingsAbsolute = apiCost - actualCost;
  
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-semibold text-slate-700">Cost Analysis</h3>
        {cacheHit && (
          <div className="flex items-center gap-1.5 px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 12v3c0 1.657 3.134 3 7 3s7-1.343 7-3v-3c0 1.657-3.134 3-7 3s-7-1.343-7-3z" />
              <path d="M3 7v3c0 1.657 3.134 3 7 3s7-1.343 7-3V7c0 1.657-3.134 3-7 3S3 8.657 3 7z" />
              <path d="M17 5c0 1.657-3.134 3-7 3S3 6.657 3 5s3.134-3 7-3 7 1.343 7 3z" />
            </svg>
            CACHED
          </div>
        )}
      </div>
      
      <div className="space-y-4">
        {/* Actual Cost */}
        <div>
          <div className="flex items-baseline justify-between mb-1">
            <span className="text-xs font-medium text-slate-600">Routed Cost</span>
            <span className="text-3xl font-bold text-slate-900">${actualCost.toFixed(4)}</span>
          </div>
        </div>

        {/* Comparison Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-600">vs API-only</span>
            <span className="text-slate-400 line-through">${apiCost.toFixed(4)}</span>
          </div>
          
          {/* Visual comparison bar */}
          <div className="relative h-2 bg-slate-100 rounded-full overflow-hidden">
            <div 
              className="absolute left-0 top-0 h-full bg-gradient-to-r from-green-500 to-emerald-500"
              style={{ width: `${Math.max((actualCost / apiCost) * 100, 5)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-slate-500">
            <span>Routed</span>
            <span>API-only baseline</span>
          </div>
        </div>

        {/* Savings */}
        <div className="pt-4 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-medium text-green-700 mb-0.5">Cost Saved</div>
              <div className="text-xs text-slate-600">${savingsAbsolute.toFixed(4)} saved</div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-green-600">{costSaved.toFixed(0)}%</span>
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}