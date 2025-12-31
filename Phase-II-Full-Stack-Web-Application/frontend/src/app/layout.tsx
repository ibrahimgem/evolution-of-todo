import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/context/ThemeContext";
import ErrorBoundary from "@/components/common/ErrorBoundary";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "Evolution of Todo - Modern Task Management",
    template: "%s | Evolution of Todo",
  },
  description: "A beautifully designed todo application with full-stack capabilities - Manage your tasks with elegance and style.",
  keywords: ["todo", "tasks", "productivity", "task management", "organize"],
  authors: [{ name: "Evolution of Todo" }],
  openGraph: {
    title: "Evolution of Todo - Modern Task Management",
    description: "A beautifully designed todo application to help you stay organized and productive.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="min-h-screen">
        {/* Background orbs for ambient lighting */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-200/30 dark:bg-primary-800/20 rounded-full blur-3xl animate-float" />
          <div className="absolute top-1/2 -left-40 w-80 h-80 bg-success-200/20 dark:bg-success-800/15 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
          <div className="absolute -bottom-40 right-1/3 w-96 h-96 bg-warning-200/20 dark:bg-warning-800/15 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
        </div>

        {/* Glass overlay for depth */}
        <div className="fixed inset-0 bg-gradient-to-br from-white/40 via-white/20 to-transparent dark:from-gray-900/40 dark:via-gray-900/20 dark:to-transparent pointer-events-none z-0" />

        <ErrorBoundary>
          <ThemeProvider>
            <div className="relative z-10">
              {children}
            </div>
          </ThemeProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
