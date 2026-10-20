import { useState } from "react";
import { generateTests } from "./api";
import {
  Code2,
  Play,
  Sparkles,
  CheckCircle,
  Bug,
  ShieldCheck,
} from "lucide-react";

export default function App() {
  const [code, setCode] = useState(
    "def divide(a, b):\n    return a / b"
  );
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerateTests = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await generateTests(code);
      setResult(data);
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Unable to connect to the Django API."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-5 md:px-8">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-violet-600 p-2 text-white">
              <Code2 size={24} />
            </div>
            <span className="text-xl font-bold tracking-tight">
              TestPilot <span className="text-violet-600">AI</span>
            </span>
          </div>

          <div className="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Testing Agent
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-10 md:px-8 md:py-14">
        <section className="mb-9">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-violet-100 bg-violet-50 px-3 py-1.5 text-xs font-bold tracking-wider text-violet-700">
            <Sparkles size={15} />
            MOCK-BASED AUTOMATION
          </div>

          <h1 className="text-3xl font-bold tracking-tight md:text-5xl">
            Automated Software Testing
          </h1>

          <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-500 md:text-base">
            Generate test cases, execute supported Python functions,
            inspect failures, and build an automated testing workflow.
          </p>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          {/* Source code panel */}
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
              <h2 className="flex items-center gap-2 font-semibold">
                <Code2 size={19} className="text-violet-600" />
                Source Code
              </h2>
              <span className="rounded-md bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600">
                Python
              </span>
            </div>

            <div className="p-5">
              <textarea
                aria-label="Python source code"
                value={code}
                onChange={(event) => setCode(event.target.value)}
                spellCheck={false}
                className="min-h-72 w-full resize-y rounded-xl border border-slate-700 bg-slate-950 p-5 font-mono text-sm leading-7 text-emerald-300 outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
                placeholder="Enter your Python source code..."
              />

              <button
                onClick={handleGenerateTests}
                disabled={loading || !code.trim()}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-5 py-3.5 font-semibold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Play size={17} />
                {loading ? "Running Tests..." : "Generate & Run Tests"}
              </button>

              <p className="mt-3 text-xs leading-5 text-slate-400">
                Mock test generation and execution are connected to Django REST APIs.
              </p>
            </div>
          </div>

          {/* Test results panel */}
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
              <h2 className="flex items-center gap-2 font-semibold">
                <Bug size={19} className="text-violet-600" />
                Test Results
              </h2>
              <span className="rounded-md bg-slate-100 px-3 py-1.5 text-xs text-slate-500">
                Workspace
              </span>
            </div>

            <div className="flex min-h-80 flex-col items-center px-6 py-10 text-center">
              {error ? (
                <>
                  <div className="rounded-full bg-red-50 p-4 text-red-600">
                    <Bug size={30} />
                  </div>
                  <h3 className="mt-5 text-lg font-bold">Request failed</h3>
                  <p className="mt-2 text-sm text-red-600">{error}</p>
                </>
              ) : result ? (
                <>
                  <div className="rounded-full bg-emerald-50 p-4 text-emerald-600">
                    <CheckCircle size={30} />
                  </div>

                  <h3 className="mt-5 text-lg font-bold">
                    Tests executed
                  </h3>
                  <p className="mt-2 text-sm text-slate-600">
                    {result.message}
                  </p>

                  <div className="mt-5 grid w-full grid-cols-3 gap-2 text-left">
                    <div className="rounded-lg bg-slate-50 p-3">
                      <p className="text-xs text-slate-500">Generated</p>
                      <p className="mt-1 text-xl font-bold">
                        {result.total ?? result.tests?.length ?? 0}
                      </p>
                    </div>
                    <div className="rounded-lg bg-emerald-50 p-3">
                      <p className="text-xs text-slate-500">Passed</p>
                      <p className="mt-1 text-xl font-bold text-emerald-700">
                        {result.passed ?? 0}
                      </p>
                    </div>
                    <div className="rounded-lg bg-red-50 p-3">
                      <p className="text-xs text-slate-500">Failed</p>
                      <p className="mt-1 text-xl font-bold text-red-700">
                        {result.failed ?? 0}
                      </p>
                    </div>
                  </div>

                  <div className="mt-5 w-full space-y-2 text-left">
                    {result.results?.map((test, index) => (
                      <div
                        key={`${test.name}-${index}`}
                        className="rounded-lg border border-slate-200 p-3"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-sm font-medium">
                            {test.name}
                          </span>
                          <span
                            className={
                              test.status === "passed"
                                ? "text-sm font-semibold text-emerald-600"
                                : "text-sm font-semibold text-red-600"
                            }
                          >
                            {test.status}
                          </span>
                        </div>

                        {test.message && (
                          <p className="mt-1 text-xs text-slate-500">
                            {test.message}
                          </p>
                        )}

                        {test.status === "failed" && (
                          <div className="mt-2 text-xs text-slate-600">
                            <p>Expected: {String(test.expected ?? "N/A")}</p>
                            <p>Actual: {String(test.actual ?? "N/A")}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => {
                      setResult(null);
                      setError("");
                    }}
                    className="mt-5 text-sm font-semibold text-violet-600 hover:text-violet-800"
                  >
                    Reset results
                  </button>
                </>
              ) : (
                <>
                  <div className="rounded-2xl bg-violet-50 p-5 text-violet-600">
                    <Sparkles size={30} />
                  </div>
                  <h3 className="mt-5 text-lg font-bold">
                    Ready to test your code?
                  </h3>
                  <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
                    Enter supported Python code and start your testing workflow.
                  </p>
                </>
              )}
            </div>

            {/* Dashboard summary */}
            <div className="grid grid-cols-3 border-t border-slate-200">
              {["Generated", "Passed", "Failed"].map((label) => (
                <div
                  key={label}
                  className="border-r border-slate-200 p-4 last:border-r-0"
                >
                  <p className="text-xs text-slate-500">{label}</p>
                  <p className="mt-2 text-2xl font-bold text-slate-800">
                    {label === "Generated"
                      ? result?.total ?? result?.tests?.length ?? "—"
                      : label === "Passed"
                      ? result?.passed ?? "—"
                      : result?.failed ?? "—"}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <footer className="mt-8 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
          <span className="flex items-center gap-2">
            <ShieldCheck size={16} className="text-emerald-600" />
            TestPilot AI · Development Mode
          </span>
          <span>React.js + Tailwind CSS</span>
        </footer>
      </main>
    </div>
  );
}