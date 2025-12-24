import type { GenerateRequest, GenerateResponse } from '../types/api';

const API_BASE = 'http://localhost:8000';

export async function generateResponse(request: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export function calculateApiCost(tokens: { input: number; output: number }): number {
  // GPT-4 pricing: $0.03 per 1K input, $0.06 per 1K output
  const inputCost = (tokens.input / 1000) * 0.03;
  const outputCost = (tokens.output / 1000) * 0.06;
  return inputCost + outputCost;
}

export function getConfidenceBand(confidence: number): string {
  if (confidence >= 0.7) return 'high';
  if (confidence >= 0.45) return 'medium';
  return 'low';
}