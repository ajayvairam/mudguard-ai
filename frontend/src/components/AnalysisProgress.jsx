import React, { useEffect, useState } from 'react';
import { CheckCircle2, CircleDot, Circle, Loader2 } from 'lucide-react';

const STEPS = [
  "Upload complete",
  "Extracting prescription text",
  "Identifying medicines",
  "Checking duplicate medicines",
  "Checking drug interactions",
  "Checking dosage concerns",
  "Preparing summary"
];

export default function AnalysisProgress({ currentStep = 3, onComplete }) {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStepIndex((prev) => {
        if (prev < STEPS.length - 1) {
          return prev + 1;
        } else {
          clearInterval(timer);
          if (onComplete) setTimeout(onComplete, 500);
          return prev;
        }
      });
    }, 650);

    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-xl max-w-lg mx-auto">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 rounded-full bg-teal-50 text-teal-600 flex items-center justify-center">
          <Loader2 className="w-5 h-5 animate-spin" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900">Analysing Prescriptions</h3>
          <p className="text-xs text-slate-500">Cross-referencing trusted drug safety databases...</p>
        </div>
      </div>

      <div className="space-y-3.5">
        {STEPS.map((label, idx) => {
          const isDone = idx < stepIndex;
          const isCurrent = idx === stepIndex;
          const isPending = idx > stepIndex;

          return (
            <div
              key={label}
              className={`flex items-center space-x-3 text-sm font-medium transition-all duration-300 ${
                isDone
                  ? 'text-teal-800'
                  : isCurrent
                  ? 'text-slate-900 font-bold scale-[1.02]'
                  : 'text-slate-400'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-5 h-5 text-teal-600 shrink-0" />
              ) : isCurrent ? (
                <CircleDot className="w-5 h-5 text-teal-600 animate-pulse shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-slate-300 shrink-0" />
              )}
              <span>{label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
