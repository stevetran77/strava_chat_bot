/**
 * Adapted from "AI Prompt Composer with Model Selector" by neeraj singh (@hellocloud.webdev),
 * https://21st.dev/@hellocloud.webdev/components/ai-prompt-composer-with-model-selector
 * Licensed under the MIT License (as stated on the component's 21st.dev page).
 * Changes: model list comes from the API, "effort" maps to the model's thinking mode, demo-only parts removed.
 */
'use client';

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';

// Adapted from the "AI prompt composer with model selector" design for the local COROS chat:
// the model list comes from the API (settings), "effort" maps to the model's thinking mode,
// and the demo-only parts (mode menu, theme switch, upgrade banner, tour, voice, files) are removed.

export type EffortLevel = 'Standard' | 'Thinking';

export interface ComposerModel {
  id: string;
  name: string;
}

export interface AIComposerSubmission {
  prompt: string;
  modelId: string;
  modelName: string;
  effort: EffortLevel;
  /** True when the model should use its thinking mode (slower, maybe better). */
  think: boolean;
}

export interface AIComposerProps {
  /** Models the user may pick, normally fetched from the API. */
  models: ComposerModel[];
  /** Model selected first; falls back to the first model. */
  defaultModelId?: string;
  /** Called with the trimmed prompt and the chosen model and effort. */
  onSubmit: (submission: AIComposerSubmission) => void;
  /** Blocks submitting (for example while an answer is loading). */
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

const EFFORTS: EffortLevel[] = ['Standard', 'Thinking'];

function Chevron() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true" style={{ color: 'var(--ink-muted)' }}>
      <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Check() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true" className="flex-shrink-0">
      <path d="M3.2 8.5L6.5 11.8L13 4.5" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function AIComposer({
  models,
  defaultModelId,
  onSubmit,
  disabled = false,
  placeholder = 'Ask about your training…',
  className = '',
}: AIComposerProps) {
  const [promptText, setPromptText] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeModelId, setActiveModelId] = useState(defaultModelId ?? models[0]?.id ?? '');
  const [efforts, setEfforts] = useState<Record<string, EffortLevel>>({});
  const [hoveredModelId, setHoveredModelId] = useState<string | null>(null);
  const hideTimerRef = useRef<number | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Models arrive after the first render; pick the default once they do.
  useEffect(() => {
    if (!models.some((m) => m.id === activeModelId)) {
      setActiveModelId(defaultModelId ?? models[0]?.id ?? '');
    }
  }, [models, defaultModelId, activeModelId]);

  useEffect(() => {
    const close = () => {
      setMenuOpen(false);
      setHoveredModelId(null);
    };
    window.addEventListener('click', close);
    return () => window.removeEventListener('click', close);
  }, []);

  const activeModel = useMemo(() => models.find((m) => m.id === activeModelId), [models, activeModelId]);
  const effortOf = useCallback((id: string): EffortLevel => efforts[id] ?? 'Standard', [efforts]);
  const hoveredIndex = models.findIndex((m) => m.id === hoveredModelId);
  const canSubmit = !disabled && promptText.trim().length > 0 && activeModel !== undefined;

  const clearHideTimer = () => {
    if (hideTimerRef.current !== null) window.clearTimeout(hideTimerRef.current);
    hideTimerRef.current = null;
  };
  const scheduleHide = () => {
    clearHideTimer();
    hideTimerRef.current = window.setTimeout(() => setHoveredModelId(null), 80);
  };

  const submit = () => {
    const prompt = promptText.trim();
    if (!canSubmit || !activeModel) return;
    const effort = effortOf(activeModel.id);
    onSubmit({ prompt, modelId: activeModel.id, modelName: activeModel.name, effort, think: effort === 'Thinking' });
    setPromptText('');
    textareaRef.current?.focus();
  };

  const selectModel = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setActiveModelId(id);
    setMenuOpen(false);
    setHoveredModelId(null);
  };

  const selectEffort = (e: React.MouseEvent, id: string, effort: EffortLevel) => {
    e.stopPropagation();
    setEfforts((prev) => ({ ...prev, [id]: effort }));
    setActiveModelId(id);
  };

  const toggleMenu = (e: React.MouseEvent) => {
    e.stopPropagation();
    setMenuOpen((open) => !open);
    setHoveredModelId(null);
  };

  return (
    <div className={`aic-root w-full ${className}`}>
      <style>{`
        .aic-root { --aic-card: var(--panel); --aic-pill-hover: rgb(255 255 255 / 0.06); --aic-hover: rgb(255 255 255 / 0.07); }
        .aic-card { position: relative; border-radius: 24px; border: 1px solid var(--line-strong); background: var(--aic-card);
          padding: 16px 14px 12px 16px; transition: border-color .16s ease, box-shadow .16s ease; }
        .aic-card:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgb(184 169 255 / 0.18); }
        .aic-input { width: 100%; background: transparent; border: 0; outline: none; resize: none; color: var(--ink); font: inherit;
          line-height: 1.5; min-height: 28px; max-height: 140px; field-sizing: content; padding: 0 2px; margin-bottom: 12px; }
        .aic-input::placeholder { color: var(--ink-muted); opacity: 1; }
        .aic-model-btn { height: 38px; border-radius: 9999px; padding: 0 12px; display: inline-flex; align-items: center; gap: 8px;
          background: transparent; border: 1px solid transparent; color: var(--ink); font: inherit; font-weight: 500; cursor: pointer;
          transition: background-color .2s ease, border-color .2s ease; }
        .aic-model-btn:hover, .aic-model-btn[aria-expanded="true"] { background: var(--aic-pill-hover); border-color: var(--line); }
        .aic-popover { position: absolute; left: 0; bottom: 46px; z-index: 30; border-radius: 18px; padding: 8px;
          background: var(--panel-solid); border: 1px solid var(--line-strong); box-shadow: 0 22px 48px -10px rgb(0 0 0 / 0.65);
          transform-origin: bottom left; transition: opacity .18s var(--ease), transform .2s var(--ease); }
        .aic-popover[data-open="false"] { opacity: 0; transform: translateY(6px) scale(.97); pointer-events: none; }
        .aic-popover[data-open="true"] { opacity: 1; transform: none; }
        .aic-row { height: 38px; padding: 0 12px; border-radius: 12px; display: flex; align-items: center; justify-content: space-between;
          gap: 8px; width: 100%; background: transparent; border: 0; color: var(--ink); font: inherit; font-size: 14.5px; text-align: left; cursor: pointer; }
        .aic-row:hover, .aic-row[data-hover="true"] { background: var(--aic-hover); }
        .aic-effort::before { content: ""; position: absolute; top: -8px; bottom: -8px; left: -16px; width: 16px; }
        .aic-send { width: 38px; height: 38px; border-radius: 9999px; border: 1px solid var(--line); background: var(--raised); color: var(--ink-muted);
          display: inline-flex; align-items: center; justify-content: center; cursor: pointer; transition: all .18s ease; }
        .aic-send[data-ready="true"] { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
        .aic-send:disabled { cursor: default; opacity: .6; }
      `}</style>

      <section className="aic-card">
        <textarea
          ref={textareaRef}
          rows={1}
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              submit();
            }
          }}
          className="aic-input"
          placeholder={placeholder}
          aria-label="Câu hỏi"
          autoFocus
        />

        <div className="flex items-center justify-between gap-2">
          <div className="relative inline-flex items-center">
            <button
              type="button"
              onClick={toggleMenu}
              disabled={models.length === 0}
              className="aic-model-btn"
              aria-haspopup="menu"
              aria-expanded={menuOpen}
            >
              <span className="whitespace-nowrap">{activeModel?.name ?? 'Đang tải model…'}</span>
              {activeModel && <span style={{ color: 'var(--ink-muted)', fontWeight: 400 }}>{effortOf(activeModel.id)}</span>}
              <Chevron />
            </button>

            <div
              className="aic-popover w-[240px]"
              data-open={menuOpen}
              role="menu"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex flex-col gap-0.5">
                {models.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    role="menuitem"
                    className="aic-row"
                    data-hover={m.id === hoveredModelId}
                    onClick={(e) => selectModel(e, m.id)}
                    onMouseEnter={() => {
                      clearHideTimer();
                      setHoveredModelId(m.id);
                    }}
                    onMouseLeave={scheduleHide}
                  >
                    <span className="truncate">
                      {m.name} <span style={{ color: 'var(--ink-muted)' }}>{effortOf(m.id)}</span>
                    </span>
                    {m.id === activeModelId && <Check />}
                  </button>
                ))}
              </div>
            </div>

            {/* Effort submenu: appears beside the hovered model and tracks its row. */}
            <div
              className="aic-popover aic-effort w-[150px]"
              data-open={menuOpen && hoveredIndex >= 0}
              role="menu"
              style={{ left: 250, bottom: 46 + Math.max(0, models.length - 1 - hoveredIndex) * 40 }}
              onClick={(e) => e.stopPropagation()}
              onMouseEnter={clearHideTimer}
              onMouseLeave={scheduleHide}
            >
              <div className="px-3 py-1.5 text-[13px] font-medium" style={{ color: 'var(--ink-soft)' }}>
                Chế độ
              </div>
              {hoveredModelId &&
                EFFORTS.map((level) => (
                  <button
                    key={level}
                    type="button"
                    role="menuitemradio"
                    aria-checked={effortOf(hoveredModelId) === level}
                    className="aic-row"
                    onClick={(e) => selectEffort(e, hoveredModelId, level)}
                  >
                    <span>{level}</span>
                    {effortOf(hoveredModelId) === level && <Check />}
                  </button>
                ))}
            </div>
          </div>

          <button type="button" onClick={submit} disabled={!canSubmit} data-ready={canSubmit} className="aic-send" aria-label="Gửi">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path d="M8 12.8V3.2M8 3.2L3.8 7.4M8 3.2L12.2 7.4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </section>
    </div>
  );
}
