'use client';

import { ReactNode } from 'react';

interface ConfidenceFieldProps {
  id: string;
  label: string;
  confidence?: number;
  /** Span full grid width (e.g., for textareas) */
  fullWidth?: boolean;
  children: ReactNode;
}

const LOW_CONFIDENCE_THRESHOLD = 0.85;

export default function ConfidenceField({
  id,
  label,
  confidence,
  fullWidth = false,
  children,
}: ConfidenceFieldProps) {
  // undefined = confidence unknown → treat as low confidence (amber by default)
  const isLowConfidence =
    confidence === undefined || confidence < LOW_CONFIDENCE_THRESHOLD;

  return (
    <div className={fullWidth ? 'sm:col-span-2' : ''}>
      <label
        htmlFor={id}
        className="flex items-center gap-1 text-xs font-medium text-slate-700 dark:text-slate-300 mb-1"
      >
        {label}
        {isLowConfidence && (
          <span
            className="text-amber-400 cursor-help"
            title="Baja confianza OCR — verificar manualmente"
            aria-label="Baja confianza OCR — verificar manualmente"
            role="img"
          >
            ⚠
          </span>
        )}
        {confidence !== undefined && (
          <span className="ml-auto text-slate-400 text-xs font-normal">
            {Math.round(confidence * 100)}%
          </span>
        )}
      </label>
      <div
        className={
          isLowConfidence
            ? 'rounded-md border-2 border-amber-400'
            : ''
        }
      >
        {children}
      </div>
    </div>
  );
}
