import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { flushSync } from "react-dom";

export const THEMES = ["dark", "light"];
const STORAGE_KEY = "coros-chat-theme";

// Saved choice first, then the system setting, else dark (the original look).
export function initialTheme() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (THEMES.includes(saved)) return saved;
  } catch { /* storage can be blocked */ }
  return window.matchMedia?.("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

const ThemeContext = createContext({ theme: "dark", setTheme: () => {} });

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Browsers without View Transitions cross-fade the colours that can be animated, for as long as the fade lasts.
function fadeFallback() {
  const root = document.documentElement;
  root.classList.add("theme-fading");
  setTimeout(() => root.classList.remove("theme-fading"), 650);
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(initialTheme);
  // The whole page cross-fades from the old theme to the new one (see ::view-transition in styles.css), so dark to light
  // is a slow dissolve instead of a flash.
  const setTheme = useCallback((next) => {
    const apply = () => { document.documentElement.dataset.theme = next; setThemeState(next); };
    if (document.documentElement.dataset.theme === next) return;
    if (document.startViewTransition) {
      let applied = false;
      document.startViewTransition(() => { applied = true; flushSync(apply); });
      setTimeout(() => { if (!applied) apply(); }, 1200); // never leave the switch dead if the browser skips the callback
    }
    else { if (!reducedMotion()) fadeFallback(); apply(); }
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem(STORAGE_KEY, theme); } catch { /* ignore */ }
  }, [theme]);
  const value = useMemo(() => ({ theme, setTheme }), [theme, setTheme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);
