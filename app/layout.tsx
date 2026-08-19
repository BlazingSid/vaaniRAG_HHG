import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAGInGoa Voice Search",
  description: "A grounded multilingual voice RAG system over AI4Bharat MSMARCO-XI.",
  other: { "codex-preview": "development" },
  icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
