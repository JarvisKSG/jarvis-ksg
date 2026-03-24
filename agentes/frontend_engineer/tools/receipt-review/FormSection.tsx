'use client';

import { ReactNode } from 'react';

interface FormSectionProps {
  title: string;
  children: ReactNode;
}

export default function FormSection({ title, children }: FormSectionProps) {
  return (
    <fieldset className="mb-6">
      <legend className="
        w-full text-xs font-semibold uppercase tracking-wider
        text-slate-500 dark:text-slate-400
        border-b border-slate-200 dark:border-slate-700
        pb-1 mb-4
      ">
        {title}
      </legend>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {children}
      </div>
    </fieldset>
  );
}
