'use client';

interface ReceiptImagePanelProps {
  imageUrl?: string | null;
}

export default function ReceiptImagePanel({ imageUrl }: ReceiptImagePanelProps) {
  return (
    <div className="flex flex-col h-full min-h-64 lg:min-h-0">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 mb-3">
        Recibo escaneado / Scanned Receipt
      </h2>
      <div
        className="
          flex-1 flex flex-col items-center justify-center
          rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700
          bg-slate-50 dark:bg-slate-800/50
          min-h-64 p-8 gap-4
        "
        role="img"
        aria-label="Vista previa del recibo escaneado"
      >
        {imageUrl ? (
          // When a real image URL is provided, display it
          // Using a regular img tag here since next/image requires static analysis
          // In production, swap for next/image with appropriate width/height
          <img
            src={imageUrl}
            alt="Recibo escaneado"
            className="max-w-full max-h-full object-contain rounded-lg"
          />
        ) : (
          <>
            <svg
              className="w-16 h-16 text-slate-300 dark:text-slate-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <div className="text-center">
              <p className="text-sm font-medium text-slate-400 dark:text-slate-500">
                Recibo escaneado
              </p>
              <p className="text-xs text-slate-400 dark:text-slate-600 mt-1">
                Scanned Receipt
              </p>
            </div>
            <p className="text-xs text-slate-400 dark:text-slate-600 text-center">
              La imagen del recibo se mostrará aquí una vez procesada por el extractor OCR.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
