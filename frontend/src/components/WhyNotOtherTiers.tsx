import type { DebugInfo, ModelTier } from '../types/api';

interface WhyNotOtherTiersProps {
  debug: DebugInfo;
  modelUsed: ModelTier;
}

interface TierReason {
  tier: ModelTier;
  selected: boolean;
  reason: string;
  icon: 'check' | 'warning' | 'info';
}

export default function WhyNotOtherTiers({ debug, modelUsed }: WhyNotOtherTiersProps) {
  const reasons: TierReason[] = [];

  // Small tier
  if (modelUsed === 'small') {
    reasons.push({
      tier: 'small',
      selected: true,
      reason: 'Selected: Sufficient for this task based on classifier prediction and token limits',
      icon: 'check',
    });
  } else if (debug.context_window?.escalated_from === 'small') {
    reasons.push({
      tier: 'small',
      selected: false,
      reason: `Rejected: Context window overflow (${debug.context_window.total_tokens} > 2048 tokens)`,
      icon: 'warning',
    });
  } else if (debug.classifier && debug.classifier.predicted_task !== 'classification') {
    reasons.push({
      tier: 'small',
      selected: false,
      reason: `Not suitable: Task type is "${debug.classifier.predicted_task}", not classification`,
      icon: 'info',
    });
  } else if (debug.classifier && debug.classifier.confidence < 0.45) {
    reasons.push({
      tier: 'small',
      selected: false,
      reason: 'Not suitable: Low classifier confidence, escalated for safety',
      icon: 'info',
    });
  }

  // Medium tier
  if (modelUsed === 'medium') {
    reasons.push({
      tier: 'medium',
      selected: true,
      reason: 'Selected: Balanced choice for this complexity and confidence level',
      icon: 'check',
    });
  } else if (modelUsed === 'small') {
    reasons.push({
      tier: 'medium',
      selected: false,
      reason: 'Not needed: Task is simple enough for small model',
      icon: 'info',
    });
  } else if (debug.context_window?.escalated_from === 'medium') {
    reasons.push({
      tier: 'medium',
      selected: false,
      reason: `Rejected: Context window overflow (${debug.context_window.total_tokens} > 4096 tokens)`,
      icon: 'warning',
    });
  }

  // API tier
  if (modelUsed === 'api') {
    let reason = 'Selected: ';
    if (debug.static_rule?.route_to === 'api') {
      reason += 'High risk level requires external API';
    } else if (debug.heuristics?.override === 'context_too_large') {
      reason += 'Context size exceeds local model capabilities';
    } else if (debug.context_window?.warning) {
      reason += 'Context exceeds even API limits (truncation may occur)';
    } else if (debug.classifier && debug.classifier.confidence < 0.45) {
      reason += 'Low confidence requires most capable model';
    } else {
      reason += 'Most capable model needed for this task';
    }
    reasons.push({
      tier: 'api',
      selected: true,
      reason,
      icon: 'check',
    });
  } else {
    reasons.push({
      tier: 'api',
      selected: false,
      reason: 'Not needed: Local models are sufficient for this task (cost-effective)',
      icon: 'info',
    });
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">Why This Model?</h3>
      
      <div className="space-y-3">
        {reasons.map((item, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border-2 ${
              item.selected
                ? 'bg-blue-50 border-blue-200'
                : 'bg-slate-50 border-slate-200'
            }`}
          >
            <div className="flex items-start gap-3">
              {/* Icon */}
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                item.icon === 'check' ? 'bg-blue-500' :
                item.icon === 'warning' ? 'bg-orange-500' :
                'bg-slate-400'
              }`}>
                {item.icon === 'check' && (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {item.icon === 'warning' && (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                )}
                {item.icon === 'info' && (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`font-semibold uppercase text-xs tracking-wide ${
                    item.tier === 'small' ? 'text-blue-700' :
                    item.tier === 'medium' ? 'text-purple-700' :
                    'text-orange-700'
                  }`}>
                    {item.tier}
                  </span>
                  {item.selected && (
                    <span className="px-2 py-0.5 bg-blue-600 text-white rounded text-xs font-medium">
                      SELECTED
                    </span>
                  )}
                </div>
                <p className={`text-sm ${
                  item.selected ? 'text-blue-900' : 'text-slate-600'
                }`}>
                  {item.reason}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}