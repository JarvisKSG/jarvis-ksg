'use client';

interface MathValidationBannerProps {
  hasMismatch: boolean;
  computed: number;
  declared: number;
}

function formatCOP(value: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export default function MathValidationBanner({
  hasMismatch,
  computed,
  declared,
}: MathValidationBannerProps) {
  if (!hasMismatch) return null;

  return (
    <div
      role="alert"
      aria-live="polite"
      className="
        flex items-start gap-3 rounded-lg border border-red-400
        bg-red-500/10 dark:bg-red-500/20 px-4 py-3 mb-4
      "
    >
      <span className="text-red-400 text-base leading-none mt-0.5" aria-hidden="true">
        ⚠
      </span>
      <p className="text-sm text-red-400 font-medium">
        Discrepancia: Subtotal + IVA ({formatCOP(computed)}) &ne; Total Original (
        {formatCOP(declared)}). Verifique los campos.
      </p>
    </div>
  );
}
