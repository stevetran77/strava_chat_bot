import { createContext, useContext, useEffect, useMemo, useState } from "react";

export const LANGS = ["vi", "en"];
const STORAGE_KEY = "coros-chat-lang";

export const TEXT = {
  vi: {
    subtitle: "Dữ liệu của bạn, xử lý hoàn toàn trên máy này",
    language: "Ngôn ngữ giao diện",
    lightMode: "Chế độ sáng",
    englishInterface: "Giao diện tiếng Anh",
    conversation: "Cuộc trò chuyện",
    welcomeTitle: "Hỏi về những buổi tập của bạn",
    welcomeBody: "Số km, pace, tải tập luyện, biểu đồ theo tuần hoặc tháng, và gợi ý dựa trên chính dữ liệu COROS của bạn.",
    examples: [
      "Tuần này tôi chạy bao nhiêu km?",
      "Vẽ biểu đồ số km chạy mỗi tuần trong 1 tháng gần nhất",
      "Tỉ lệ tải gần đây của tôi có ổn không, tuần sau nên tập thế nào?",
      "Tháng nào tôi chạy nhiều km nhất?",
    ],
    placeholder: "Hỏi bằng tiếng Việt hoặc English…",
    working: "Đang xử lý",
    retry: "Thử lại",
    toolsUsed: (n) => `Công cụ đã dùng (${n})`,
    sqlLabel: "Câu truy vấn SQL",
    codeLabel: "Mã vẽ biểu đồ",
    argsLabel: (name) => `Tham số của ${name}`,
    chartLoading: "Đang tải biểu đồ…",
    dataTable: (n) => `Bảng số liệu (${n} dòng)`,
    dataTableLabel: (title) => `Số liệu của biểu đồ ${title}`,
    chartLabel: (kind, title) => `Biểu đồ ${kind === "line" ? "đường" : "cột"}: ${title}. Xem bảng số liệu bên dưới.`,
    composer: { question: "Câu hỏi", send: "Gửi", loadingModel: "Đang tải model…", mode: "Chế độ", effort: { Standard: "Tiêu chuẩn", Thinking: "Suy nghĩ sâu" } },
    errors: {
      400: "Câu hỏi không hợp lệ. Hãy diễn đạt lại rồi gửi lại.",
      gateway: "Chưa kết nối được máy chủ API. Kiểm tra uvicorn đã chạy chưa, rồi bấm Thử lại.",
      server: "Máy chủ gặp lỗi khi xử lý câu hỏi này. Bấm Thử lại, hoặc diễn đạt lại câu hỏi.",
      other: (status) => `Máy chủ trả lỗi ${status}. Bấm Thử lại.`,
      network: "Không kết nối được máy chủ. Kiểm tra mạng nội bộ và uvicorn, rồi bấm Thử lại.",
    },
  },
  en: {
    subtitle: "Your data, processed entirely on this machine",
    language: "Interface language",
    lightMode: "Light mode",
    englishInterface: "English interface",
    conversation: "Conversation",
    welcomeTitle: "Ask about your workouts",
    welcomeBody: "Distance, pace, training load, charts by week or month, and suggestions based on your own COROS data.",
    examples: [
      "How many km did I run this week?",
      "Plot my weekly running km for the last month",
      "Is my recent training load OK, and how should I train next week?",
      "Which month did I run the most km?",
    ],
    placeholder: "Ask in English or Tiếng Việt…",
    working: "Working",
    retry: "Try again",
    toolsUsed: (n) => `Tools used (${n})`,
    sqlLabel: "SQL query",
    codeLabel: "Chart code",
    argsLabel: (name) => `Arguments of ${name}`,
    chartLoading: "Loading chart…",
    dataTable: (n) => `Data table (${n} rows)`,
    dataTableLabel: (title) => `Data of the chart ${title}`,
    chartLabel: (kind, title) => `${kind === "line" ? "Line" : "Bar"} chart: ${title}. See the data table below.`,
    composer: { question: "Question", send: "Send", loadingModel: "Loading models…", mode: "Mode", effort: { Standard: "Standard", Thinking: "Deep thinking" } },
    errors: {
      400: "That question is not valid. Rephrase it and send it again.",
      gateway: "Cannot reach the API server. Check that uvicorn is running, then press Try again.",
      server: "The server failed on this question. Press Try again, or rephrase it.",
      other: (status) => `The server returned error ${status}. Press Try again.`,
      network: "Cannot reach the server. Check the local network and uvicorn, then press Try again.",
    },
  },
};

// Saved choice first, then the browser language, else English.
function initialLang() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (LANGS.includes(saved)) return saved;
  } catch { /* storage can be blocked */ }
  return navigator.language?.toLowerCase().startsWith("vi") ? "vi" : "en";
}

const LangContext = createContext({ lang: "en", setLang: () => {}, t: TEXT.en });

export function LangProvider({ children }) {
  const [lang, setLang] = useState(initialLang);
  useEffect(() => {
    document.documentElement.lang = lang;
    try { localStorage.setItem(STORAGE_KEY, lang); } catch { /* ignore */ }
  }, [lang]);
  const value = useMemo(() => ({ lang, setLang, t: TEXT[lang] }), [lang]);
  return <LangContext.Provider value={value}>{children}</LangContext.Provider>;
}

export const useLang = () => useContext(LangContext);

// Error messages are built outside React, so they take the dictionary as an argument.
export function describeFailure(t, error) {
  const { errors } = t;
  if (error.status === 400) return errors[400];
  if ([502, 503, 504].includes(error.status)) return errors.gateway;
  if (error.status >= 500) return errors.server;
  if (error.status) return errors.other(error.status);
  return errors.network;
}
