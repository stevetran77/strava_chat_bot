import { lazy, Suspense, useEffect, useRef, useState } from "react";
import Particles from "./Particles";
import AIComposer from "./components/ui/ai-prompt-composer-with-model-selector";
import { describeFailure, useLang } from "./i18n";
import SquishSwitch from "./SquishSwitch";
import { useTheme } from "./theme";

// The chart library is only fetched when an answer contains a chart.
const Chart = lazy(() => import("./Chart"));

// Particles are white on the dark page and violet on the light one.
const PARTICLES = {
  dark: { colors: ["#ffffff", "#ffffff", "#ffffff"], glow: 0.5, opacity: 1 },
  light: { colors: ["#6a56e6", "#6a56e6", "#6a56e6"], glow: 0.25, opacity: 0.6 },
};

// Both header switches share one size, one palette and one motion; the active option sits on the accent thumb.
const SWITCH = { trackColor: "var(--switch-track)", thumbColor: "var(--accent)", activeColor: "var(--accent-ink)", idleColor: "var(--ink-muted)",
  width: 76, height: 38, radius: 19, stretch: 44, speed: 50, hoverScale: 1.04, colorDuration: 320 };

const Sun = () => <svg width="18" height="18" viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="8" cy="8" r="2.8" stroke="currentColor" strokeWidth="1.5" /><path d="M8 1.5v1.6M8 12.9v1.6M1.5 8h1.6M12.9 8h1.6M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg>;
const Moon = () => <svg width="18" height="18" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M13.2 9.6A5.6 5.6 0 0 1 6.4 2.8a5.6 5.6 0 1 0 6.8 6.8Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" /></svg>;

async function sendQuestion(t, question, conversationId, options) {
  let response;
  try {
    response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, conversation_id: conversationId, ...options }),
    });
  } catch {
    throw new Error(describeFailure(t, {}));
  }
  if (!response.ok) throw new Error(describeFailure(t, { status: response.status }));
  return response.json();
}

// Models come from the server settings; if the call fails the composer stays empty and the server default is used.
async function loadModels() {
  const response = await fetch("/api/models");
  if (!response.ok) throw new Error(`models ${response.status}`);
  return response.json();
}

// The glass sheen follows the pointer: the pointer position inside the box is exposed as CSS variables.
function follow(event) {
  const box = event.currentTarget.getBoundingClientRect();
  event.currentTarget.style.setProperty("--mx", `${event.clientX - box.left}px`);
  event.currentTarget.style.setProperty("--my", `${event.clientY - box.top}px`);
}

const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const Chevron = () => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M4 2.5 7.5 6 4 9.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
);
const ArrowRight = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8h9.5M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
);
const ArrowUp = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true"><path d="M9 14.5V4M4.5 8.5 9 4l4.5 4.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
);

function ToolDetails({ tools }) {
  const { t } = useLang();
  if (!tools.length) return null;
  return (
    <details className="details">
      <summary><Chevron />{t.toolsUsed(tools.length)}</summary>
      {tools.map((tool, index) => (
        <div key={index} className="tool">
          <strong>{tool.name}</strong> <span className="muted">→ {tool.summary}</span>
          {tool.arguments.sql && <pre tabIndex={0} role="region" aria-label={t.sqlLabel}>{tool.arguments.sql}</pre>}
          {tool.arguments.code && <pre tabIndex={0} role="region" aria-label={t.codeLabel}>{tool.arguments.code}</pre>}
          {!tool.arguments.sql && !tool.arguments.code && <pre tabIndex={0} role="region" aria-label={t.argsLabel(tool.name)}>{JSON.stringify(tool.arguments, null, 2)}</pre>}
        </div>
      ))}
    </details>
  );
}

function Message({ message, rowRef, onRetry }) {
  const { t } = useLang();
  if (message.role === "user") return <div className="row user" ref={rowRef}><div className="bubble user" onPointerMove={follow}>{message.text}</div></div>;
  return (
    <div className="row" ref={rowRef}>
      <div className={`bubble ${message.error ? "error" : ""}`} role={message.error ? "alert" : undefined} onPointerMove={follow}>
        <div className="bubble-fold"><div className="bubble-inner">
        <p className="text">{message.text}</p>
        {message.error && onRetry && <button type="button" className="retry" onClick={onRetry}>{t.retry}</button>}
        {message.charts?.map((spec, index) => (
          <Suspense key={index} fallback={<div className="chart-loading" role="status">{t.chartLoading}</div>}><Chart spec={spec} /></Suspense>
        ))}
        {message.sources?.length > 0 && (
          <ul className="sources">
            {[...new Map(message.sources.map((card) => [card.source_url, card])).values()].map((card) => (
              <li key={card.source_url}>
                <a href={card.source_url} target="_blank" rel="noreferrer">{card.topic}</a>
                {card.consensus_level !== "consensus" && <span className="tag">{card.consensus_level}</span>}
              </li>
            ))}
          </ul>
        )}
        {message.tools && <ToolDetails tools={message.tools} />}
        </div></div>
      </div>
    </div>
  );
}

export default function App() {
  const { lang, setLang, t } = useLang();
  const { theme, setTheme } = useTheme();
  const look = PARTICLES[theme];
  const [messages, setMessages] = useState([]);
  const [models, setModels] = useState({ default: undefined, list: [] });
  const [busy, setBusy] = useState(false);
  const conversationId = useRef(null);
  const lastRow = useRef(null);
  const bottom = useRef(null);

  useEffect(() => {
    loadModels()
      .then((data) => setModels({ default: data.default, list: data.models.map((id) => ({ id, name: id })) }))
      .catch(() => {});
  }, []);

  // A new answer is read from its first line; the user's own message and the working indicator sit at the end.
  useEffect(() => {
    const last = messages[messages.length - 1];
    const behavior = prefersReducedMotion() ? "auto" : "smooth";
    if (last?.role === "assistant" && !busy) lastRow.current?.scrollIntoView({ block: "start", behavior });
    else bottom.current?.scrollIntoView({ block: "end", behavior });
  }, [messages, busy]);

  async function ask(question, options = {}) {
    const text = question.trim();
    if (!text || busy) return;
    setBusy(true);
    setMessages((current) => [...current, { role: "user", text }]);
    try {
      const data = await sendQuestion(t, text, conversationId.current, options);
      conversationId.current = data.conversation_id;
      setMessages((current) => [...current, { role: "assistant", ...data }]);
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", error: true, text: error.message, retryQuestion: text, retryOptions: options }]);
    } finally {
      setBusy(false);
    }
  }

  // Retry replaces the failed exchange instead of stacking a second copy of the question.
  function retry(index) {
    const { retryQuestion, retryOptions } = messages[index];
    setMessages((current) => current.slice(0, index - 1));
    ask(retryQuestion, retryOptions);
  }

  return (
    <>
    <Particles particleColors={look.colors} particleCount={200} particleSpread={10} speed={0.1} particleBaseSize={100}
      glow={look.glow} twinkle={0.3} moveParticlesOnHover hoverEffect="parallax" sizeRandomness={1} shape="circle"
      particleHoverFactor={1} clickBurst intro opacity={look.opacity} />
    <div className="app">
      <header>
        <h1>COROS Chat</h1>
        <span className="muted">{t.subtitle}</span>
        <div className="controls">
          <SquishSwitch checked={lang === "en"} onChange={(english) => setLang(english ? "en" : "vi")} label={t.englishInterface}
            startContent="VI" endContent="EN" {...SWITCH} />
          <SquishSwitch checked={theme === "light"} onChange={(light) => setTheme(light ? "light" : "dark")} label={t.lightMode}
            startContent={<Moon />} endContent={<Sun />} {...SWITCH} />
        </div>
      </header>
      <main role="log" aria-label={t.conversation} aria-busy={busy}>
        {messages.length === 0 && (
          <section className="welcome">
            <div className="welcome-intro">
              <h2>{t.welcomeTitle}</h2>
              <p>{t.welcomeBody}</p>
            </div>
            <div className="prompts">
              {t.examples.map((example) => <button key={example} type="button" onClick={() => ask(example)}><span>{example}</span><ArrowRight /></button>)}
            </div>
          </section>
        )}
        {messages.map((message, index) => (
          <Message key={index} message={message} rowRef={index === messages.length - 1 ? lastRow : undefined}
            onRetry={message.retryQuestion && index === messages.length - 1 && !busy ? () => retry(index) : undefined} />
        ))}
        {busy && <div className="row"><div className="bubble"><div className="working"><i /><i /><i /><i /><i /><span>{t.working}</span></div></div></div>}
        <div ref={bottom} />
      </main>
      <form onSubmit={(event) => event.preventDefault()}>
        <AIComposer models={models.list} defaultModelId={models.default} disabled={busy}
          placeholder={t.placeholder} labels={t.composer}
          onSubmit={({ prompt, modelId, think }) => ask(prompt, { model: modelId, think })} />
      </form>
    </div>
    </>
  );
}
