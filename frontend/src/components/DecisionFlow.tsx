import type { DebugInfo, ModelTier } from '../types/api';
import ModelBadge from './ModelBadge';

interface DecisionFlowProps {
  debug: DebugInfo;
  finalModel: ModelTier;
}

interface FlowStep {
  label: string;
  status: 'accepted' | 'skipped' | 'evaluated';
  model?: ModelTier;
  detail?: string;
  icon: 'check' | 'skip' | 'info';
}

export default function DecisionFlow({ debug, finalModel }: DecisionFlowProps) {
  const steps: FlowStep[] = [];

  // Step 1: Static Rule
  if (debug.static_rule) {
    steps.push({
      label: 'Static Rule',
      status: 'accepted',
      model: debug.static_rule.route_to as ModelTier,
      detail: debug.static_rule.rule_name.replace(/_/g, ' '),
      icon: 'check',
    });
  } else {
    steps.push({
      label: 'Static Rule',
      status: 'skipped',
      detail: 'No matching rule',
      icon: 'skip',
    });
  }

  // Step 2: Heuristics
  if (debug.heuristics?.override) {
    const heuristicModel = debug.heuristics.override === 'context_too_large' ? 'api' : 'medium';
    steps.push({
      label: 'Heuristic Override',
      status: 'accepted',
      model: heuristicModel as ModelTier,
      detail: debug.heuristics.override.replace(/_/g, ' '),
      icon: 'check',
    });
  } else {
    steps.push({
      label: 'Heuristic',
      status: 'evaluated',
      detail: `Context: ${debug.heuristics?.context_ratio || 0}%, Weight: ${debug.heuristics?.generation_weight || 'unknown'}`,
      icon: 'info',
    });
  }

  // Step 3: Classifier
  if (debug.classifier) {
    const confidence = debug.classifier.confidence;
    const confidenceBand = confidence >= 0.7 ? 'High' : confidence >= 0.45 ? 'Medium' : 'Low';
    
    steps.push({
      label: 'ML Classifier',
      status: 'accepted',
      detail: `${debug.classifier.predicted_task} • ${confidenceBand} confidence (${(confidence * 100).toFixed(0)}%)`,
      icon: 'check',
    });
  }

  // Step 4: Context Window
  if (debug.context_window?.overflow) {
    steps.push({
      label: 'Context Window Safety',
      status: 'accepted',
      model: finalModel,
      detail: `Escalated from ${debug.context_window.escalated_from} (overflow detected)`,
      icon: 'check',
    });
  } else if (debug.context_window) {
    steps.push({
      label: 'Context Window Safety',
      status: 'evaluated',
      detail: `${debug.context_window.total_tokens}/${debug.context_window.max_allowed} tokens (passed)`,
      icon: 'info',
    });
  }

  // Final step
  steps.push({
    label: 'Final Selection',
    status: 'accepted',
    model: finalModel,
    detail: 'Routed successfully',
    icon: 'check',
  });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-6">Decision Flow</h3>
      
      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-5 top-8 bottom-8 w-0.5 bg-slate-200" />

        {/* Steps */}
        <div className="space-y-6">
          {steps.map((step, index) => (
            <div key={index} className="relative flex items-start gap-4">
              {/* Node */}
              <div className={`relative z-10 w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                step.status === 'accepted' ? 'bg-blue-500 border-blue-500' :
                step.status === 'skipped' ? 'bg-white border-slate-300' :
                'bg-slate-100 border-slate-300'
              }`}>
                {step.icon === 'check' && (
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {step.icon === 'skip' && (
                  <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
                {step.icon === 'info' && (
                  <svg className="w-5 h-5 text-slate-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 pt-1 pb-2">
                <div className="flex items-center gap-3 mb-1">
                  <span className={`font-semibold ${
                    step.status === 'accepted' ? 'text-slate-900' :
                    step.status === 'skipped' ? 'text-slate-400' :
                    'text-slate-700'
                  }`}>
                    {step.label}
                  </span>
                  {step.model && <ModelBadge model={step.model} size="sm" />}
                  {step.status === 'accepted' && !step.model && (
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                      ACTIVE
                    </span>
                  )}
                  {step.status === 'skipped' && (
                    <span className="px-2 py-0.5 bg-slate-100 text-slate-500 rounded text-xs font-medium">
                      SKIPPED
                    </span>
                  )}
                </div>
                <p className={`text-sm ${
                  step.status === 'accepted' ? 'text-slate-600' :
                  step.status === 'skipped' ? 'text-slate-400' :
                  'text-slate-500'
                }`}>
                  {step.detail}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}