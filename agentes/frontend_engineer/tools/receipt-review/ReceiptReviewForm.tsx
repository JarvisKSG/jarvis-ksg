'use client';

import { useReducer, useMemo } from 'react';
import ReceiptImagePanel from './ReceiptImagePanel';
import FormSection from './FormSection';
import ConfidenceField from './ConfidenceField';
import MathValidationBanner from './MathValidationBanner';
import {
  CajaNegraRow,
  FormAction,
  FormState,
  ReceiptReviewFormProps,
  SUBCATEGORIA_OPTIONS,
  ESTADO_OPTIONS,
  METODO_PAGO_OPTIONS,
  DIVISA_OPTIONS,
  PROYECTO_OPTIONS,
} from './ReceiptReviewForm.types';

// ---------- Shared input class ----------
const INPUT_BASE =
  'w-full rounded-md border border-slate-200 dark:border-slate-700 ' +
  'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 ' +
  'text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500 ' +
  'disabled:bg-slate-100 dark:disabled:bg-slate-700 disabled:text-slate-400 ' +
  'disabled:cursor-not-allowed';

// ---------- Reducer ----------
function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value };
    case 'RESET':
      return action.payload;
    default:
      return state;
  }
}

// ---------- Main component ----------
export default function ReceiptReviewForm({
  initialData,
  confidence,
  onSave,
  imageUrl,
  confianzaGlobal,
}: ReceiptReviewFormProps) {
  const [state, dispatch] = useReducer(formReducer, initialData);

  const set = (field: keyof CajaNegraRow) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const raw = e.target.value;
      const numericFields: (keyof CajaNegraRow)[] = ['subtotal', 'iva', 'trm'];
      dispatch({
        type: 'SET_FIELD',
        field,
        value: numericFields.includes(field) ? (raw === '' ? null : Number(raw)) : raw || null,
      });
    };

  // Computed fields (never editable)
  const computedTotalOrig = useMemo(
    () => (state.subtotal ?? 0) + (state.iva ?? 0),
    [state.subtotal, state.iva],
  );

  const computedTotalCop = useMemo(() => {
    if (state.divisa === 'COP' || !state.divisa) return computedTotalOrig;
    return computedTotalOrig * (state.trm ?? 1);
  }, [computedTotalOrig, state.divisa, state.trm]);

  const declaredTotalOrig = state.totalOrig ?? 0;
  const hasMismatch =
    declaredTotalOrig !== 0 && computedTotalOrig !== declaredTotalOrig;

  const isForeign = state.divisa && state.divisa !== 'COP';

  const REQUIRED_FIELDS: (keyof CajaNegraRow)[] = ['fecha', 'proveedor', 'concepto', 'subcategoria', 'estado'];
  const missingRequired = REQUIRED_FIELDS.some(f => !state[f]);

  const handleSave = () => {
    if (missingRequired || hasMismatch) return;
    const row: CajaNegraRow = {
      fecha: state.fecha ?? '',
      idUnico: state.idUnico ?? '',
      idFactura: state.idFactura ?? null,
      proveedor: state.proveedor ?? '',
      nit: state.nit ?? null,
      subcategoria: (state.subcategoria as CajaNegraRow['subcategoria']) ?? 'OP',
      proyecto: state.proyecto ?? null,
      concepto: state.concepto ?? '',
      subtotal: state.subtotal ?? 0,
      iva: state.iva ?? 0,
      totalOrig: computedTotalOrig,
      divisa: state.divisa ?? 'COP',
      trm: isForeign ? (state.trm ?? null) : null,
      totalCop: computedTotalCop,
      metodoPago: state.metodoPago ?? null,
      estado: (state.estado as CajaNegraRow['estado']) ?? 'pendiente',
      idConciliacion: state.idConciliacion ?? null,
      comprobante: state.comprobante ?? null,
      archivo: state.archivo ?? null,
      notas: state.notas ?? null,
    };
    onSave(row);
  };

  const c = (field: keyof CajaNegraRow) => confidence[field];

  return (
    <div className="min-h-screen bg-slate-900 p-4 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-xl font-bold text-slate-100 mb-6">
          Revisión de Recibo / Receipt Review
        </h1>

        {confianzaGlobal !== undefined && (
          <div className="mb-4 flex items-center gap-2">
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
              Confianza OCR:
            </span>
            <span className={`text-sm font-semibold ${
              confianzaGlobal >= 0.85
                ? 'text-emerald-400'
                : confianzaGlobal >= 0.70
                ? 'text-amber-400'
                : 'text-red-400'
            }`}>
              {Math.round(confianzaGlobal * 100)}%
            </span>
          </div>
        )}

        {/* Split-screen layout */}
        <div className="flex flex-col lg:flex-row gap-6">

          {/* LEFT: Image panel */}
          <div className="w-full lg:w-1/2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
            <ReceiptImagePanel imageUrl={imageUrl} />
          </div>

          {/* RIGHT: Scrollable form */}
          <div className="w-full lg:w-1/2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 overflow-y-auto max-h-screen lg:max-h-[calc(100vh-8rem)]">

            <MathValidationBanner hasMismatch={hasMismatch} computed={computedTotalOrig} declared={declaredTotalOrig} />

            {/* SECTION 1: IDENTIFICACION */}
            <FormSection title="Identificación">
              <ConfidenceField id="fecha" label="Fecha *" confidence={c('fecha')}>
                <input id="fecha" type="date" required className={INPUT_BASE}
                  value={state.fecha ?? ''} onChange={set('fecha')} />
              </ConfidenceField>

              <ConfidenceField id="idUnico" label="ID Unico (sistema)" confidence={c('idUnico')}>
                <input id="idUnico" type="text" readOnly className={INPUT_BASE}
                  value={state.idUnico ?? ''} aria-readonly="true" tabIndex={-1} />
              </ConfidenceField>

              <ConfidenceField id="idFactura" label="ID Factura" confidence={c('idFactura')}>
                <input id="idFactura" type="text" className={INPUT_BASE}
                  value={state.idFactura ?? ''} onChange={set('idFactura')}
                  placeholder="Ej: F-2026-001" />
              </ConfidenceField>

              <ConfidenceField id="proveedor" label="Proveedor *" confidence={c('proveedor')}>
                <input id="proveedor" type="text" required className={INPUT_BASE}
                  value={state.proveedor ?? ''} onChange={set('proveedor')} />
              </ConfidenceField>

              <ConfidenceField id="nit" label="NIT" confidence={c('nit')}>
                <input id="nit" type="text" className={INPUT_BASE}
                  value={state.nit ?? ''} onChange={set('nit')}
                  placeholder="Ej: 900.123.456-7" />
              </ConfidenceField>
            </FormSection>

            {/* SECTION 2: CLASIFICACION */}
            <FormSection title="Clasificación">
              <ConfidenceField id="subcategoria" label="Subcategoria *" confidence={c('subcategoria')}>
                <select id="subcategoria" required className={INPUT_BASE}
                  value={state.subcategoria ?? ''} onChange={set('subcategoria')}>
                  <option value="">— Seleccionar —</option>
                  {SUBCATEGORIA_OPTIONS.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </ConfidenceField>

              <ConfidenceField id="proyecto" label="Proyecto" confidence={c('proyecto')}>
                <select id="proyecto" className={INPUT_BASE}
                  value={state.proyecto ?? ''} onChange={set('proyecto')}>
                  <option value="">— Ninguno —</option>
                  {PROYECTO_OPTIONS.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </ConfidenceField>

              <ConfidenceField id="concepto" label="Concepto *" confidence={c('concepto')} fullWidth>
                <textarea id="concepto" required rows={3} className={INPUT_BASE}
                  value={state.concepto ?? ''} onChange={set('concepto')}
                  placeholder="Descripción del gasto..." />
              </ConfidenceField>
            </FormSection>

            {/* SECTION 3: VALORES */}
            <FormSection title="Valores">
              <ConfidenceField id="subtotal" label="Subtotal (COP) *" confidence={c('subtotal')}>
                <input id="subtotal" type="number" required min={0} className={INPUT_BASE}
                  value={state.subtotal ?? ''} onChange={set('subtotal')} />
              </ConfidenceField>

              <ConfidenceField id="iva" label="IVA (COP) *" confidence={c('iva')}>
                <input id="iva" type="number" required min={0} className={INPUT_BASE}
                  value={state.iva ?? ''} onChange={set('iva')} />
              </ConfidenceField>

              <ConfidenceField id="totalOrig" label="Total Original (calculado)" confidence={c('totalOrig')}>
                <input id="totalOrig" type="number" readOnly className={INPUT_BASE}
                  value={computedTotalOrig} aria-readonly="true" tabIndex={-1} />
              </ConfidenceField>

              <ConfidenceField id="divisa" label="Divisa *" confidence={c('divisa')}>
                <select id="divisa" required className={INPUT_BASE}
                  value={state.divisa ?? 'COP'} onChange={set('divisa')}>
                  {DIVISA_OPTIONS.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </ConfidenceField>

              {isForeign && (
                <ConfidenceField id="trm" label="TRM" confidence={c('trm')}>
                  <input id="trm" type="number" min={0} step="0.01" className={INPUT_BASE}
                    value={state.trm ?? ''} onChange={set('trm')}
                    placeholder="Ej: 4200.50" />
                </ConfidenceField>
              )}

              <ConfidenceField id="totalCop" label="Total COP (calculado)" confidence={c('totalCop')}>
                <input id="totalCop" type="number" readOnly className={INPUT_BASE}
                  value={computedTotalCop} aria-readonly="true" tabIndex={-1} />
              </ConfidenceField>
            </FormSection>

            {/* SECTION 4: ADMINISTRATIVO */}
            <FormSection title="Administrativo">
              <ConfidenceField id="metodoPago" label="Método de Pago" confidence={c('metodoPago')}>
                <select id="metodoPago" className={INPUT_BASE}
                  value={state.metodoPago ?? ''} onChange={set('metodoPago')}>
                  <option value="">— Seleccionar —</option>
                  {METODO_PAGO_OPTIONS.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </ConfidenceField>

              <ConfidenceField id="estado" label="Estado *" confidence={c('estado')}>
                <select id="estado" required className={INPUT_BASE}
                  value={state.estado ?? 'pendiente'} onChange={set('estado')}>
                  {ESTADO_OPTIONS.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </ConfidenceField>

              <ConfidenceField id="idConciliacion" label="ID Conciliación" confidence={c('idConciliacion')}>
                <input id="idConciliacion" type="text" className={INPUT_BASE}
                  value={state.idConciliacion ?? ''} onChange={set('idConciliacion')} />
              </ConfidenceField>

              <ConfidenceField id="comprobante" label="Comprobante (URL)" confidence={c('comprobante')}>
                <input id="comprobante" type="url" className={INPUT_BASE}
                  value={state.comprobante ?? ''} onChange={set('comprobante')}
                  placeholder="https://..." />
              </ConfidenceField>

              <ConfidenceField id="archivo" label="Archivo Drive" confidence={c('archivo')}>
                <input id="archivo" type="text" className={INPUT_BASE}
                  value={state.archivo ?? ''} onChange={set('archivo')}
                  placeholder="Keystone/Contabilidad/..." />
              </ConfidenceField>

              <ConfidenceField id="notas" label="Notas" confidence={c('notas')} fullWidth>
                <textarea id="notas" rows={2} className={INPUT_BASE}
                  value={state.notas ?? ''} onChange={set('notas')} />
              </ConfidenceField>
            </FormSection>

            {/* Save button */}
            <div className="mt-2 flex justify-end">
              <button
                type="button"
                onClick={handleSave}
                disabled={hasMismatch || missingRequired}
                className="
                  px-6 py-2 rounded-lg text-sm font-semibold
                  bg-emerald-500 hover:bg-emerald-400 text-white
                  focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2
                  disabled:opacity-40 disabled:cursor-not-allowed
                  transition-colors
                "
                aria-disabled={hasMismatch || missingRequired}
              >
                Guardar Recibo
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
