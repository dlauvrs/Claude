'use client';

import { useState } from 'react';
import { LoadingSpinner } from './LoadingSpinner';

interface PriceFormProps {
  jobId: string;
  suggestedPrice: number;
  onSuccess?: (action: 'approve' | 'reject') => void;
}

export function PriceForm({ jobId, suggestedPrice, onSuccess }: PriceFormProps) {
  const [price, setPrice] = useState(suggestedPrice.toString());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  async function submit(action: 'approve' | 'reject') {
    setError(null);
    setLoading(true);
    try {
      const parsedPrice = parseFloat(price.replace(',', '.'));
      if (action === 'approve' && (isNaN(parsedPrice) || parsedPrice <= 0)) {
        setError('Informe um preço válido.');
        return;
      }
      const res = await fetch('/api/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jobId, price: parsedPrice, action }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error ?? `Erro ${res.status}`);
      }
      setDone(true);
      onSuccess?.(action);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <div className="rounded-lg bg-green-50 p-4 text-center text-green-700">
        Resposta enviada com sucesso!
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Preço de Venda (R$)
        </label>
        <div className="flex items-center gap-2">
          <span className="text-gray-500">R$</span>
          <input
            type="number"
            min="0"
            step="0.01"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-lg focus:border-blue-500 focus:outline-none"
            placeholder="0,00"
          />
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Sugerido pela IA: R$ {suggestedPrice.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-3">
        <button
          onClick={() => submit('approve')}
          disabled={loading}
          className="flex flex-1 items-center justify-center gap-2 rounded-md bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? <LoadingSpinner size="sm" /> : null}
          Aprovar e Publicar
        </button>
        <button
          onClick={() => submit('reject')}
          disabled={loading}
          className="rounded-md border border-red-200 px-4 py-2 font-medium text-red-600 transition hover:bg-red-50 disabled:opacity-50"
        >
          Rejeitar
        </button>
      </div>
    </div>
  );
}
