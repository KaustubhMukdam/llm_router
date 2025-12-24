// src/components/ModelBadge.tsx
import type { ModelTier } from '../types/api';

interface ModelBadgeProps {
  model: ModelTier;
  size?: 'sm' | 'md';
}

export default function ModelBadge({ model, size = 'md' }: ModelBadgeProps) {
  const colors = {
    small: 'bg-blue-100 text-blue-700 border-blue-200',
    medium: 'bg-purple-100 text-purple-700 border-purple-200',
    api: 'bg-orange-100 text-orange-700 border-orange-200',
  };

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span className={`inline-flex items-center gap-1.5 ${sizeClasses} border rounded-full font-semibold ${colors[model]}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {model.toUpperCase()}
    </span>
  );
}