import { useEffect, useRef, useState } from "react";

const MAX_ROWS = 6;

const ArrowUp = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M9 14.5V4M4.5 8.5 9 4l4.5 4.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
);

/**
 * Question box: text area, model picker and a thinking switch.
 * Props: models [{id, name}], defaultModelId, disabled, placeholder, onSubmit({prompt, modelId, think}).
 * Enter sends, Shift+Enter adds a line.
 */
export default function Composer({ models, defaultModelId, disabled, placeholder, onSubmit }) {
  const [text, setText] = useState("");
  const [modelId, setModelId] = useState(defaultModelId ?? "");
  const [think, setThink] = useState(false);
  const area = useRef(null);
  const activeModel = models.some((model) => model.id === modelId) ? modelId : (defaultModelId ?? models[0]?.id ?? "");
  const canSend = !disabled && text.trim().length > 0;

  // The text area grows with its content up to MAX_ROWS lines, then scrolls.
  useEffect(() => {
    const node = area.current;
    if (!node) return;
    node.style.height = "auto";
    const line = parseFloat(getComputedStyle(node).lineHeight);
    node.style.height = `${Math.min(node.scrollHeight, line * MAX_ROWS)}px`;
  }, [text]);

  // Focus returns to the box when an answer arrives, so the next question can be typed at once.
  useEffect(() => { if (!disabled) area.current?.focus(); }, [disabled]);

  function send() {
    if (!canSend) return;
    onSubmit({ prompt: text.trim(), modelId: activeModel, think });
    setText("");
  }

  return (
    <div className="composer">
      <textarea ref={area} rows={1} value={text} placeholder={placeholder} aria-label="Câu hỏi" autoFocus
        onChange={(event) => setText(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); send(); }
        }} />
      <div className="composer-bar">
        {models.length > 0 && (
          <select value={activeModel} onChange={(event) => setModelId(event.target.value)} aria-label="Model" disabled={disabled}>
            {models.map((model) => <option key={model.id} value={model.id}>{model.name}</option>)}
          </select>
        )}
        <button type="button" className="think" aria-pressed={think} onClick={() => setThink((on) => !on)} title="Bật chế độ suy nghĩ: chậm hơn, có thể chính xác hơn">
          Suy nghĩ sâu
        </button>
        <button className="send" type="button" onClick={send} disabled={!canSend} aria-label="Gửi"><ArrowUp /></button>
      </div>
    </div>
  );
}
