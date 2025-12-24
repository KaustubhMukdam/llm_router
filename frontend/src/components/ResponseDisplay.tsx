// src/components/ResponseDisplay.tsx
import type { ModelTier } from '../types/api';
import ModelBadge from './ModelBadge';

interface ResponseDisplayProps {
  response: string;
  modelUsed: ModelTier;
}

export default function ResponseDisplay({ response, modelUsed }: ResponseDisplayProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Generated Response</h3>
        <ModelBadge model={modelUsed} />
      </div>
      
      <div className="prose prose-slate max-w-none">
        <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 whitespace-pre-wrap text-slate-800">
          {response}
        </div>
      </div>
    </div>
  );
}