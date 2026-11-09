import { lazy, Suspense, useEffect, useRef, useState } from "react";
import Particles from "./Particles";
import Composer from "./Composer";

// The chart library is only fetched when an answer contains a chart.
const Chart = lazy(() => import("./Chart"));

// The page is one dark world: white particles on a deep aubergine page.
const PARTICLE_COLORS = ["#ffffff", "#ffffff", "#ffffff"];

const EXAMPLES = [
  "Tuần này tôi chạy bao nhiêu km?",
  "Vẽ biểu đồ số km chạy mỗi tuần trong 12 tuần gần nhất",
  "Tỉ lệ tải gần đây của tôi có ổn không, tuần sau nên tập thế nào?",
  "Which month did I run the most km?",
];

// Each failure gets a message that names the problem and the way out.
function describeFailure(error) {
  if (error.status === 400) return "Câu hỏi không hợp lệ. Hãy diễn đạt lại rồi gửi lại.";
  if (error.status === 502 || error.status === 503 || error.status === 504) return "Chưa kết nối được máy chủ API. Kiểm tra uvicorn đã chạy chưa, rồi bấm Thử lại.";
  if (error.status >= 500) return "Máy chủ gặp lỗi khi xử lý câu hỏi này. Bấm Thử lại, hoặc diễn đạt lại câu hỏi.";
  if (error.status) return `Máy chủ trả lỗi ${error.status}. Bấm Thử lại.`;
  return "Không kết nối được máy chủ. Kiểm tra mạng nội bộ và uvicorn, rồi bấm Thử lại.";
}

async function sendQuestion(question, conversationId, options) {
  let response;
  try {
    response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, conversation_id: conversationId, ...options }),
    });
  } catch {
    throw new Error(describeFailure({}));
  }
  if (!response.ok) throw new Error(describeFailure({ status: response.status }));
  return response.json();
}

// Models come from the server settings; if the call fails the composer stays empty and the server default is used.
async function loadModels() {
  const response = await fetch("/api/models");
  if (!response.ok) throw new Error(`models ${response.status}`);
  return response.json();
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
  if (!tools.length) return null;
  return (
    <details className="details">
      <summary><Chevron />Công cụ đã dùng ({tools.length})</summary>
      {tools.map((tool, index) => (
        <div key={index} className="tool">
          <strong>{tool.name}</strong> <span className="muted">→ {tool.summary}</span>
          {tool.arguments.sql && <pre tabIndex={0} role="region" aria-label="Câu truy vấn SQL">{tool.arguments.sql}</pre>}
          {tool.arguments.code && <pre tabIndex={0} role="region" aria-label="Mã vẽ biểu đồ">{tool.arguments.code}</pre>}
          {!tool.arguments.sql && !tool.arguments.code && <pre tabIndex={0} role="region" aria-label={`Tham số của ${tool.name}`}>{JSON.stringify(tool.arguments, null, 2)}</pre>}
        </div>
      ))}
    </details>
  );
}

function Message({ message, rowRef, onRetry }) {
  if (message.role === "user") return <div className="row user" ref={rowRef}><div className="bubble user">{message.text}</div></div>;
  return (
    <div className="row" ref={rowRef}>
      <div className={`bubble ${message.error ? "error" : ""}`} role={message.error ? "alert" : undefined}>
        <p className="text">{message.text}</p>
        {message.error && onRetry && <button type="button" className="retry" onClick={onRetry}>Thử lại</button>}
        {message.charts?.map((spec, index) => (
          <Suspense key={index} fallback={<div className="chart-loading" role="status">Đang tải biểu đồ…</div>}><Chart spec={spec} /></Suspense>
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
      </div>
    </div>
  );
}

export default function App() {
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
      const data = await sendQuestion(text, conversationId.current, options);
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
    <Particles particleColors={PARTICLE_COLORS} particleCount={200} particleSpread={10} speed={0.1} particleBaseSize={100}
      glow={0.5} twinkle={0.3} moveParticlesOnHover hoverEffect="parallax" sizeRandomness={1} shape="circle"
      particleHoverFactor={1} clickBurst intro opacity={1} />
    <div className="app">
      <header><h1>COROS Chat</h1><span className="muted">Dữ liệu của bạn, xử lý hoàn toàn trên máy này</span></header>
      <main role="log" aria-label="Cuộc trò chuyện" aria-busy={busy}>
        {messages.length === 0 && (
          <section className="welcome">
            <h2>Hỏi về những buổi tập của bạn</h2>
            <p>Số km, pace, tải tập luyện, biểu đồ theo tuần hoặc tháng, và gợi ý dựa trên chính dữ liệu COROS của bạn.</p>
            <div className="prompts">
              {EXAMPLES.map((example) => <button key={example} type="button" onClick={() => ask(example)}><span>{example}</span><ArrowRight /></button>)}
            </div>
          </section>
        )}
        {messages.map((message, index) => (
          <Message key={index} message={message} rowRef={index === messages.length - 1 ? lastRow : undefined}
            onRetry={message.retryQuestion && index === messages.length - 1 && !busy ? () => retry(index) : undefined} />
        ))}
        {busy && <div className="row"><div className="bubble"><div className="working"><i /><i /><i /><i /><i /><span>Đang xử lý</span></div></div></div>}
        <div ref={bottom} />
      </main>
      <form onSubmit={(event) => event.preventDefault()}>
        <Composer models={models.list} defaultModelId={models.default} disabled={busy}
          placeholder="Hỏi bằng tiếng Việt hoặc English…"
          onSubmit={({ prompt, modelId, think }) => ask(prompt, { model: modelId, think })} />
      </form>
    </div>
    </>
  );
}
