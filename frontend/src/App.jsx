import { useState, useRef } from "react";

const PINK = "#E91E63";
const PINK_LIGHT = "#fce4ec";

function StatusIcon({ type }) {
  if (type === "upload") {
    return (
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
        <path
          d="M12 16V4m0 0L8 8m4-4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2"
          stroke={PINK}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }
  if (type === "spinner") {
    return (
      <svg
        className="spinner"
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke={PINK_LIGHT}
          strokeWidth="3"
        />
        <path
          d="M12 2a10 10 0 019.95 9"
          stroke={PINK}
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
    );
  }
  if (type === "success") {
    return (
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" fill={PINK} />
        <path
          d="M8 12l3 3 5-5"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }
  if (type === "error") {
    return (
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" fill="#e53935" />
        <path
          d="M8 8l8 8M16 8l-8 8"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    );
  }
  return null;
}

function UploadZone({ onFile, disabled }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState(null);

  function handleFile(file) {
    if (file && file.name.endsWith(".csv")) {
      setFileName(file.name);
      onFile(file);
    }
  }

  return (
    <div
      className={`upload-zone ${dragOver ? "drag-over" : ""} ${disabled ? "disabled" : ""}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); if (!disabled) setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => { e.preventDefault(); setDragOver(false); if (!disabled) handleFile(e.dataTransfer.files[0]); }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        hidden
        disabled={disabled}
        onChange={(e) => handleFile(e.target.files[0])}
      />
      <StatusIcon type="upload" />
      <p className="upload-text">
        {fileName || "Clique ou arraste o CSV do teste A/B aqui"}
      </p>
      {fileName && <p className="upload-file">{fileName}</p>}
    </div>
  );
}

function ProgressBar({ label }) {
  return (
    <div className="progress-section">
      <div className="progress-bar">
        <div className="progress-fill" />
      </div>
      <p className="progress-label">{label}</p>
    </div>
  );
}

function ResultCard({ result }) {
  return (
    <div className="result-card">
      <div className="result-header">
        <StatusIcon type="success" />
        <h2>Análise concluída</h2>
      </div>

      <div className="result-body">
        <div className="result-row">
          <span className="result-label">Parceiro</span>
          <span className="result-value">{result.parceiro}</span>
        </div>
        <div className="result-row">
          <span className="result-label">Status</span>
          <span className="result-value status-ok">Sucesso</span>
        </div>
      </div>

      <div className="result-actions">
        <a href={result.pdf_url} className="btn btn-primary" download>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 16V4m0 0L8 8m4-4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          Baixar PDF
        </a>
        <a
          href={result.sheets_url}
          className="btn btn-secondary"
          target="_blank"
          rel="noopener noreferrer"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          Abrir Planilha
        </a>
      </div>
    </div>
  );
}

function ErrorCard({ message, onRetry }) {
  return (
    <div className="result-card error">
      <div className="result-header">
        <StatusIcon type="error" />
        <h2>Erro na análise</h2>
      </div>
      <p className="error-message">{message}</p>
      <div className="result-actions">
        <button className="btn btn-primary" onClick={onRetry}>
          Tentar novamente
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [phase, setPhase] = useState("upload"); // upload | processing | result | error
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [progressStep, setProgressStep] = useState("");

  const steps = [
    "Limpando dados...",
    "Calculando KPIs...",
    "Aplicando regra de decisão...",
    "Gerando narrativa com IA...",
    "Validando resposta...",
    "Montando PDF e gráficos...",
    "Atualizando planilha...",
    "Finalizando...",
  ];

  async function handleFileSelected(selectedFile) {
    setFile(selectedFile);
    setPhase("processing");
    setProgressStep(steps[0]);

    const formData = new FormData();
    formData.append("file", selectedFile);

    let stepIndex = 0;
    const progressInterval = setInterval(() => {
      stepIndex = Math.min(stepIndex + 1, steps.length - 1);
      setProgressStep(steps[stepIndex]);
    }, 5000);

    try {
      const res = await fetch("/api/analyze", { method: "POST", body: formData });
      clearInterval(progressInterval);
      setProgressStep(steps[steps.length - 1]);

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Erro ao processar análise.");
      }

      const data = await res.json();
      setTimeout(() => {
        setResult(data);
        setPhase("result");
      }, 600);
    } catch (e) {
      clearInterval(progressInterval);
      setError(e.message);
      setPhase("error");
    }
  }

  function handleNewAnalysis() {
    setPhase("upload");
    setFile(null);
    setResult(null);
    setError(null);
    setProgressStep("");
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 2L2 7l10 5 10-5-10-5z"
                stroke="white"
                strokeWidth="2"
                strokeLinejoin="round"
              />
              <path
                d="M2 17l10 5 10-5"
                stroke="white"
                strokeWidth="2"
                strokeLinejoin="round"
              />
              <path
                d="M2 12l10 5 10-5"
                stroke="white"
                strokeWidth="2"
                strokeLinejoin="round"
              />
            </svg>
            Méliuz
          </h1>
          <p className="header-sub">Análise de Teste A/B de Cashback</p>
        </div>
      </header>

      <main className="main">
        <div className="card">
          {phase === "upload" && (
            <>
              <div className="card-header">
                <h2>Nova análise</h2>
                <p className="card-desc">
                  Envie o CSV do teste A/B para gerar o relatório completo com
                  decisão, gráficos e narrativa da IA.
                </p>
              </div>
              <UploadZone onFile={handleFileSelected} disabled={false} />
            </>
          )}

          {phase === "processing" && (
            <div className="processing">
              <StatusIcon type="spinner" />
              <h2>Analisando dados...</h2>
              <ProgressBar label={progressStep} />
            </div>
          )}

          {phase === "result" && result && (
            <>
              <ResultCard result={result} />
              <div className="new-analysis-wrap">
                <button
                  className="btn btn-outline"
                  onClick={handleNewAnalysis}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 5v14m-7-7h14"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                  Nova análise
                </button>
              </div>
            </>
          )}

          {phase === "error" && (
            <>
              <ErrorCard message={error} onRetry={() => handleFileSelected(file)} />
              <div className="new-analysis-wrap">
                <button
                  className="btn btn-outline"
                  onClick={handleNewAnalysis}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 5v14m-7-7h14"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                  Nova análise
                </button>
              </div>
            </>
          )}
        </div>
      </main>

      <footer className="footer">
        <span>Gabriel Manata de Pinho</span>
        <span className="footer-sep">·</span>
        <span>Méliuz</span>
      </footer>
    </div>
  );
}
