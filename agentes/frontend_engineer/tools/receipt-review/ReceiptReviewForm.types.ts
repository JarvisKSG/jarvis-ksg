export interface CajaNegraRow {
  fecha: string;
  idUnico: string;
  idFactura: string | null;
  proveedor: string;
  nit: string | null;
  subcategoria: 'OP' | 'ADM' | 'NOM' | 'MF' | 'SP' | 'LT' | 'PROY';
  proyecto: string | null;
  concepto: string;
  subtotal: number;
  iva: number;
  totalOrig: number;
  divisa: string;
  trm: number | null;
  totalCop: number;
  metodoPago: string | null;
  estado: 'pendiente' | 'pagado' | 'anulado' | 'conciliado';
  idConciliacion: string | null;
  comprobante: string | null;
  archivo: string | null;
  notas: string | null;
}

export type FieldConfidence = Record<keyof CajaNegraRow, number>;

export interface ReceiptReviewFormProps {
  initialData: Partial<CajaNegraRow>;
  confidence: Partial<FieldConfidence>;
  onSave: (data: CajaNegraRow) => void;
  imageUrl?: string;
}

// ---------- Reducer ----------

export type FormField = keyof CajaNegraRow;

export type FormAction =
  | { type: 'SET_FIELD'; field: FormField; value: CajaNegraRow[FormField] }
  | { type: 'RESET'; payload: Partial<CajaNegraRow> };

export type FormState = Partial<CajaNegraRow>;

export const SUBCATEGORIA_OPTIONS: CajaNegraRow['subcategoria'][] = [
  'OP', 'ADM', 'NOM', 'MF', 'SP', 'LT', 'PROY',
];

export const ESTADO_OPTIONS: CajaNegraRow['estado'][] = [
  'pendiente', 'pagado', 'anulado', 'conciliado',
];

export const METODO_PAGO_OPTIONS: string[] = [
  'Transferencia', 'Efectivo', 'Tarjeta', 'Cheque', 'PSE', 'Otro',
];

export const DIVISA_OPTIONS: string[] = ['COP', 'USD', 'EUR'];

export const PROYECTO_OPTIONS: string[] = [
  'PROY-001', 'PROY-002', 'PROY-003', 'PROY-004', 'PROY-005', 'PROY-006',
];
