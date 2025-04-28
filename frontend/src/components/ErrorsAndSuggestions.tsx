import type React from "react";
import { useState } from "react";
import { FaCheckCircle, FaLightbulb } from "react-icons/fa";
import type { BpmnError } from "../types";

interface ErrorsAndSuggestionsProps {
  errors: BpmnError[] | null;
  suggestions: Suggestion[] | null;
  onApplyCorrections: (corrections: string[]) => void;
}

export interface Suggestion {
  error: string;
  correction: string;
}

const ErrorsAndSuggestions: React.FC<ErrorsAndSuggestionsProps> = ({
  errors,
  suggestions,
  onApplyCorrections,
}) => {
  const [selected, setSelected] = useState<Set<number>>(new Set());

  // Обработка чекбоксов
  const toggle = (i: number) => {
    setSelected((s) => {
      const copy = new Set(s);
      copy.has(i) ? copy.delete(i) : copy.add(i);
      return copy;
    });
  };

  const handleApply = () => {
    if (!suggestions) return;
    const toApply = Array.from(selected).map((i) => suggestions[i]?.correction);
    onApplyCorrections(toApply);
    setSelected(new Set());
  };

  if (
    (!errors || errors.length === 0) &&
    (!suggestions || suggestions.length === 0)
  )
    return null;

  return (
    <div className="mt-[4rem] flex flex-col gap-4">
      {/* Предложения */}
      {suggestions && suggestions.length > 0 && (
        <div className="rounded-lg px-5 py-4 border border-blue-200 bg-blue-50">
          <div className="flex items-center gap-2 mb-3">
            <FaLightbulb className="text-blue-500 text-xl" />
            <span className="font-semibold text-base text-blue-800">
              Предложения по исправлению
            </span>
          </div>
          <p className="text-blue-800 text-sm mb-2">
            Доступно {suggestions.length} предложений для улучшения вашей
            диаграммы
          </p>
          <ul className="mb-3">
            {suggestions.map((s, i) => (
              <li
                key={s.correction + s.error}
                className="flex items-start gap-2 mb-1"
              >
                <input
                  type="checkbox"
                  id={`sg_${i}`}
                  className="form-checkbox mt-1 accent-blue-600"
                  checked={selected.has(i)}
                  onChange={() => toggle(i)}
                />
                <label htmlFor={`sg_${i}`} className="block cursor-pointer">
                  <span className="font-medium text-blue-900">
                    {s.correction}
                  </span>
                  <div className="text-xs text-gray-500 mt-1">{s.error}</div>
                </label>
              </li>
            ))}
          </ul>
          <div className="flex justify-end mt-4">
            <button
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-md shadow disabled:opacity-60 disabled:cursor-not-allowed transition"
              disabled={selected.size === 0}
              onClick={handleApply}
            >
              <FaCheckCircle className="inline mr-2 -mt-0.5" />
              Применить выбранные ({selected.size})
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ErrorsAndSuggestions;
