
"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
};

type ConnectionState = "checking" | "online" | "offline";

const API_URL =
  process.env.NEXT_PUBLIC_AEGIS_API_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const [connection, setConnection] =
    useState<ConnectionState>("checking");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [lastChecked, setLastChecked] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function checkHealth() {
      try {
        const response = await fetch(`${API_URL}/api/v1/health`, {
          cache: "no-store",
          signal: AbortSignal.timeout(5000),
        });

        if (!response.ok) {
          throw new Error(`API returned HTTP ${response.status}`);
        }

        const data: HealthResponse = await response.json();

        if (active) {
          setHealth(data);
          setConnection("online");
          setLastChecked(new Date().toLocaleTimeString());
        }
      } catch {
        if (active) {
          setHealth(null);
          setConnection("offline");
          setLastChecked(new Date().toLocaleTimeString());
        }
      }
    }

    void checkHealth();

    const interval = window.setInterval(() => {
      void checkHealth();
    }, 15000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  const statusLabel = {
    checking: "Checking connection",
    online: "Connected",
    offline: "Unavailable",
  }[connection];

  return (
    <main className="min-h-screen bg-[#080b12] text-slate-100">
      <header className="border-b border-white/10 bg-[#0c111b]">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/30 bg-cyan-400/10 text-lg font-bold text-cyan-300">
              A
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-[0.2em]">
                AEGIS
              </h1>
              <p className="text-xs text-slate-400">
                Agentic AI Engineering, Governance, Intelligence &amp; Security
              </p>
            </div>
          </div>

          <div className="hidden rounded-full border border-white/10 px-3 py-1.5 text-xs text-slate-400 sm:block">
            LOCAL DEVELOPMENT
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-12">
        <section className="mb-10">
          <p className="mb-3 text-sm font-medium uppercase tracking-[0.25em] text-cyan-300">
            Control center
          </p>
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            System overview
          </h2>
          <p className="mt-3 max-w-2xl text-slate-400">
            Monitor AEGIS services and establish the foundation for agent
            orchestration, governance, evaluation, and security.
          </p>
        </section>

        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-300">
                API service
              </h3>
              <span
                className={`h-2.5 w-2.5 rounded-full ${
                  connection === "online"
                    ? "bg-emerald-400"
                    : connection === "offline"
                      ? "bg-rose-400"
                      : "bg-amber-400"
                }`}
              />
            </div>

            <p className="mt-5 text-2xl font-semibold">{statusLabel}</p>
            <p className="mt-2 text-sm text-slate-400">
              {health
                ? `Health endpoint reports: ${health.status}`
                : connection === "checking"
                  ? "Waiting for the health endpoint response."
                  : "Could not reach the API health endpoint."}
            </p>

            <div className="mt-6 border-t border-white/10 pt-4 text-xs text-slate-500">
              GET /api/v1/health
            </div>
          </article>

          <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <h3 className="text-sm font-medium text-slate-300">
              Agent orchestration
            </h3>
            <p className="mt-5 text-2xl font-semibold">Not initialized</p>
            <p className="mt-2 text-sm text-slate-400">
              Planner, execution, and coordination services are not connected
              to this dashboard yet.
            </p>
            <div className="mt-6 border-t border-white/10 pt-4 text-xs text-slate-500">
              Planned integration
            </div>
          </article>

          <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <h3 className="text-sm font-medium text-slate-300">
              Governance &amp; security
            </h3>
            <p className="mt-5 text-2xl font-semibold">Not initialized</p>
            <p className="mt-2 text-sm text-slate-400">
              Policy enforcement, security checks, and evaluation metrics will
              appear here as their services are implemented.
            </p>
            <div className="mt-6 border-t border-white/10 pt-4 text-xs text-slate-500">
              Planned integration
            </div>
          </article>
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-[#0c111b] p-6">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h3 className="font-medium">Connection diagnostics</h3>
              <p className="mt-1 text-sm text-slate-400">
                The API health check runs automatically every 15 seconds.
              </p>
            </div>
            <div className="text-sm text-slate-400">
              Last checked:{" "}
              <span className="text-slate-200">
                {lastChecked ?? "Waiting…"}
              </span>
            </div>
          </div>
          <p className="mt-4 break-all text-xs text-slate-500">
            API base URL: {API_URL}
          </p>
        </section>

        <footer className="mt-12 border-t border-white/10 pt-5 text-xs text-slate-500">
          AEGIS · Development environment · Dashboard foundation
        </footer>
      </div>
    </main>
  );
}
