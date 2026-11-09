import React from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/geist";
import "@fontsource-variable/geist-mono";
import App from "./App.jsx";
import { LangProvider } from "./i18n.jsx";
import { ThemeProvider } from "./theme.jsx";
import "./styles.css";

createRoot(document.getElementById("root")).render(<ThemeProvider><LangProvider><App /></LangProvider></ThemeProvider>);
