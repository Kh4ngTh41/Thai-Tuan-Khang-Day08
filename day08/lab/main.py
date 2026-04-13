import html
import json
import uuid
from http.cookies import SimpleCookie
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs

from rag_answer import rag_answer

HOST = "127.0.0.1"
PORT = 8000
SESSION_COOKIE_NAME = "rag_demo_session"
AVAILABLE_MODES = ["dense", "sparse", "hybrid"]
DEFAULT_MODES = ["dense", "sparse", "hybrid"]

# Load test questions
TEST_QUESTIONS_FILE = Path(__file__).parent / "data" / "test_questions.json"
with open(TEST_QUESTIONS_FILE, "r", encoding="utf-8") as f:
    TEST_QUESTIONS = json.load(f)

sessions: dict[str, list[dict]] = {}


def parse_cookie(cookie_header: str | None) -> dict:
    if not cookie_header:
        return {}
    cookie = SimpleCookie()
    cookie.load(cookie_header)
    return {key: morsel.value for key, morsel in cookie.items()}


def get_session_id(headers) -> str:
    cookies = parse_cookie(headers.get("Cookie"))
    session_id = cookies.get(SESSION_COOKIE_NAME)
    if session_id and session_id in sessions:
        return session_id
    session_id = str(uuid.uuid4())
    sessions[session_id] = []
    return session_id


def render_history(history: list[dict]) -> str:
    if not history:
        return ""
    items = []
    for entry in reversed(history[-10:]):
        query = html.escape(entry["query"])
        modes = html.escape(", ".join(entry["selected_modes"]))
        rerank = "Yes" if entry["use_rerank"] else "No"
        top_k_search = html.escape(str(entry.get("top_k_search", "10")))
        top_k_select = html.escape(str(entry.get("top_k_select", "3")))
        chunk_size = html.escape(str(entry.get("chunk_size", "512")))
        results = entry.get("results", [])
        
        result_details = []
        for result in results:
            mode = html.escape(result.get("mode", "").title())
            answer = html.escape(result.get("answer", "")[:200] + "..." if len(result.get("answer", "")) > 200 else result.get("answer", ""))
            sources_list = result.get("sources", [])
            sources = html.escape(", ".join(sources_list)) if sources_list else "None"
            result_details.append(f"<div style='margin-bottom: 8px;'><strong><span class='text-primary'>{mode}:</span></strong> {answer} <br><small class='text-muted'>Sources: {sources}</small></div>")
            
        details = "".join(result_details) if result_details else "No results"
        items.append(
            f"<div class=\"history-entry animate-fade-in\">"
            f"<div class=\"history-meta\">"
            f"<span class=\"tag\">Query</span> <strong>{query}</strong> &nbsp;|&nbsp; "
            f"<span class=\"tag\">Modes: {modes}</span> &nbsp;|&nbsp; "
            f"<span class=\"tag\">Rerank: {rerank}</span> &nbsp;|&nbsp; "
            f"<span class=\"tag\">Top K Search: {top_k_search}</span> &nbsp;|&nbsp; "
            f"<span class=\"tag\">Top K Select: {top_k_select}</span> &nbsp;|&nbsp; "
            f"<span class=\"tag\">Chunk Size: {chunk_size}</span>"
            f"</div>"
            f"<div class=\"history-details\">{details}</div>"
            f"</div>"
        )
    return f"<div class=\"glass-panel\" style=\"margin-top: 30px;\"><h2 class=\"section-title\">Session History</h2>{''.join(items)}</div>"


def render_page(query: str, selected_modes: list[str], use_rerank: bool, results: list[dict], history: list[dict], top_k_search: int, top_k_select: int, chunk_size: int) -> str:
    mode_checkboxes = []
    for mode in AVAILABLE_MODES:
        checked = "checked" if mode in selected_modes else ""
        mode_checkboxes.append(
            f"<label class=\"checkbox-label\">"
            f"<input type=\"checkbox\" name=\"mode\" value=\"{mode}\" {checked}>"
            f"<span>{mode.title()}</span>"
            f"</label>"
        )

    rerank_checked = "checked" if use_rerank else ""

    sample_options = []
    for q in TEST_QUESTIONS:
        sample_options.append(
            f"<option value=\"{html.escape(q['question'])}\">{html.escape(q['id'])}: {html.escape(q['question'][:60])}...</option>"
        )

    results_html = ""
    if results:
        boxes = []
        for result in results:
            answer = html.escape(result.get("answer", ""))
            sources = html.escape(", ".join(result.get("sources", [])))
            config = result.get("config", {})
            config_html = "<br>".join(
                html.escape(f"{k}: {v}") for k, v in config.items()
            )
            boxes.append(
                f"<div class=\"result-card animate-slide-up\">"
                f"<div class=\"result-card-header\">"
                f"<h2><svg width=\"24\" height=\"24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" viewBox=\"0 0 24 24\"><path stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M13 10V3L4 14h7v7l9-11h-7z\"></path></svg>{html.escape(result['mode'].title())}</h2>"
                f"</div>"
                f"<div class=\"result-meta\"><strong>Configuration</strong><br>{config_html}</div>"
                f"<div class=\"result-answer\"><strong>Answer</strong><p>{answer}</p></div>"
                f"<div class=\"result-sources\"><strong>Sources:</strong> {sources}</div>"
                f"</div>"
            )
        results_html = f"<div class=\"results-grid\">{chr(10).join(boxes)}</div>"

    history_html = render_history(history)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Nexus RAG Intelligence</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --primary-light: #e0e7ff;
      --bg-gradient-1: #f8fafc;
      --bg-gradient-2: #e2e8f0;
      --surface: rgba(255, 255, 255, 0.7);
      --surface-solid: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border-color: #cbd5e1;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      --radius-lg: 16px;
      --radius-md: 12px;
      --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    body {{ 
      font-family: 'Inter', sans-serif; 
      margin: 0; 
      padding: 0; 
      background: linear-gradient(135deg, var(--bg-gradient-1), var(--bg-gradient-2));
      background-attachment: fixed;
      color: var(--text-main);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}
    
    .container {{ max-width: 1280px; margin: 0 auto; padding: 40px 24px; }}
    
    .glass-panel {{ 
      background: var(--surface); 
      backdrop-filter: blur(16px); 
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255,255,255,0.8); 
      box-shadow: var(--shadow-lg); 
      border-radius: var(--radius-lg); 
      padding: 32px; 
      margin-bottom: 32px; 
    }}
    
    .header-section {{ text-align: center; margin-bottom: 32px; }}
    
    h1 {{ 
      font-weight: 800; 
      font-size: 3rem; 
      letter-spacing: -0.025em;
      background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin: 0 0 12px 0; 
    }}
    
    .subtitle {{ color: var(--text-muted); font-size: 1.125rem; margin: 0; }}
    .section-title {{ font-size: 1.5rem; font-weight: 700; color: var(--text-main); margin-top: 0; margin-bottom: 20px; }}
    
    .form-group {{ margin-bottom: 24px; }}
    .form-group label {{ display: block; font-weight: 600; margin-bottom: 8px; color: var(--text-main); }}
    
    textarea, input[type="number"], select {{ 
      width: 100%; 
      padding: 14px 16px; 
      border: 2px solid var(--border-color); 
      border-radius: var(--radius-md); 
      font-family: 'Inter', sans-serif; 
      font-size: 1rem; 
      background: var(--surface-solid); 
      transition: var(--transition); 
      box-sizing: border-box; 
      color: var(--text-main);
    }}
    
    textarea {{ min-height: 120px; resize: vertical; line-height: 1.5; }}
    
    textarea:focus, input[type="number"]:focus, select:focus {{ 
      outline: none; 
      border-color: var(--primary); 
      box-shadow: 0 0 0 4px var(--primary-light); 
    }}
    
    .options-grid {{ 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
      gap: 20px; 
      background: rgba(255, 255, 255, 0.4); 
      padding: 24px; 
      border-radius: var(--radius-md); 
      border: 1px solid rgba(255,255,255,0.6);
      margin-bottom: 24px;
    }}
    
    .option-item label {{ font-size: 0.875rem; color: var(--text-muted); margin-bottom: 8px; font-weight: 500; display: block; }}
    
    .checkbox-group {{ display: flex; flex-wrap: wrap; gap: 12px; }}
    
    .checkbox-label {{ 
      display: inline-flex; 
      align-items: center; 
      gap: 8px; 
      cursor: pointer; 
      font-weight: 500; 
      padding: 8px 16px; 
      background: var(--surface-solid); 
      border-radius: 9999px; 
      border: 1px solid var(--border-color); 
      transition: var(--transition); 
      font-size: 0.95rem;
      user-select: none;
    }}
    
    .checkbox-label:hover {{ border-color: var(--primary); transform: translateY(-1px); box-shadow: var(--shadow-sm); }}
    .checkbox-label input {{ accent-color: var(--primary); width: 16px; height: 16px; cursor: pointer; }}
    
    .btn-submit {{ 
      background: linear-gradient(135deg, var(--primary) 0%, #6366f1 100%); 
      color: white; 
      border: none; 
      padding: 16px 32px; 
      font-size: 1.125rem; 
      font-weight: 600; 
      border-radius: var(--radius-md); 
      cursor: pointer; 
      width: 100%; 
      transition: var(--transition); 
      box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.39); 
      display: flex; 
      justify-content: center; 
      align-items: center; 
      gap: 8px;
    }}
    
    .btn-submit:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4); }}
    .btn-submit:active {{ transform: translateY(0); }}
    .btn-submit:disabled {{ opacity: 0.7; cursor: not-allowed; transform: none; box-shadow: none; }}
    
    /* Loading overlay */
    #loading {{ 
      position: fixed; inset: 0; 
      background: rgba(255, 255, 255, 0.85); 
      backdrop-filter: blur(8px); 
      display: none; 
      justify-content: center; 
      align-items: center; 
      flex-direction: column; 
      z-index: 50; 
    }}
    
    .spinner {{ 
      width: 48px; height: 48px; 
      border: 4px solid var(--primary-light); 
      border-top-color: var(--primary); 
      border-radius: 50%; 
      animation: spin 1s linear infinite; 
      margin-bottom: 24px;
    }}
    
    .loading-text {{ font-size: 1.25rem; font-weight: 600; color: var(--primary); letter-spacing: 0.5px; }}
    
    @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
    
    /* Results Styling */
    .results-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; margin-bottom: 32px; }}
    
    .result-card {{ 
      background: var(--surface-solid); 
      border-radius: var(--radius-lg); 
      padding: 24px; 
      box-shadow: var(--shadow-md); 
      border: 1px solid rgba(0,0,0,0.05); 
      transition: var(--transition); 
      display: flex; 
      flex-direction: column;
    }}
    
    .result-card:hover {{ transform: translateY(-4px); box-shadow: var(--shadow-lg); }}
    
    .result-card h2 {{ 
      margin: 0 0 16px 0; 
      color: var(--text-main); 
      font-size: 1.25rem; 
      display: flex; 
      align-items: center; 
      gap: 10px; 
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border-color);
    }}
    
    .result-card h2 svg {{ color: var(--primary); }}
    
    .result-meta {{ 
      background: var(--bg-gradient-1); 
      padding: 12px; 
      border-radius: 8px; 
      font-size: 0.85rem; 
      color: var(--text-muted); 
      margin-bottom: 20px; 
      font-family: monospace;
      border: 1px solid var(--border-color);
    }}
    
    .result-answer {{ flex-grow: 1; margin-bottom: 20px; }}
    .result-answer strong {{ color: var(--text-main); display: block; margin-bottom: 8px; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em; }}
    .result-answer p {{ color: #334155; margin: 0; white-space: pre-line; line-height: 1.6; }}
    
    .result-sources {{ 
      padding-top: 16px; 
      border-top: 1px dashed var(--border-color); 
      font-size: 0.85rem; 
      color: var(--text-muted); 
      background: #f8fafc;
      padding: 12px;
      border-radius: 8px;
    }}
    .result-sources strong {{ color: var(--text-main); margin-right: 6px; }}
    
    /* History Styling */
    .history-entry {{ 
      padding: 20px; 
      background: var(--surface-solid); 
      border-radius: var(--radius-md); 
      margin-bottom: 16px; 
      border: 1px solid var(--border-color); 
      transition: var(--transition); 
    }}
    .history-entry:hover {{ border-color: var(--primary); box-shadow: var(--shadow-md); }}
    
    .history-meta {{ font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    
    .tag {{ 
      background: var(--primary-light); 
      color: var(--primary-hover); 
      padding: 4px 10px; 
      border-radius: 6px; 
      font-weight: 600; 
      letter-spacing: 0.025em;
    }}
    
    .history-details {{ 
      border-left: 3px solid var(--primary); 
      padding-left: 16px; 
      color: #334155; 
      font-size: 0.95rem; 
    }}
    
    .text-primary {{ color: var(--primary); }}
    .text-muted {{ color: var(--text-muted); }}
    
    /* Animations */
    .animate-fade-in {{ animation: fadeIn 0.5s ease-out; }}
    .animate-slide-up {{ animation: slideUp 0.5s ease-out forwards; opacity: 0; transform: translateY(20px); }}
    .result-card:nth-child(1) {{ animation-delay: 0.1s; }}
    .result-card:nth-child(2) {{ animation-delay: 0.2s; }}
    .result-card:nth-child(3) {{ animation-delay: 0.3s; }}
    
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @keyframes slideUp {{ to {{ opacity: 1; transform: translateY(0); }} }}
    
  </style>
</head>
<body>
  <div id="loading">
    <div class="spinner"></div>
    <div class="loading-text">Processing Query...</div>
  </div>

  <div class="container animate-fade-in">
    <div class="glass-panel">
      <div class="header-section">
        <h1>Nexus RAG Intelligence</h1>
        <p class="subtitle">Advanced Retrieval Framework &mdash; Evaluate and compare multiple search strategies.</p>
      </div>
      
      <form method="POST" onsubmit="showLoading()">
        <div class="form-group">
          <label for="query">Search Query</label>
          <textarea id="query" name="query" placeholder="Ask anything..." required>{html.escape(query)}</textarea>
        </div>
        
        <div style="display: flex; gap: 20px; margin-bottom: 24px; flex-wrap: wrap;">
          <div class="form-group" style="flex: 1 1 100%; margin-bottom: 0;">
            <label>Sample Questions</label>
            <select name="sample_query" onchange="document.getElementById('query').value = this.value">
              <option value="">-- Select a predefined query --</option>
              {''.join(sample_options)}
            </select>
          </div>
        </div>
        
        <div style="display: flex; gap: 20px; margin-bottom: 24px; flex-wrap: wrap;">
          <div class="form-group" style="flex: 1; min-width: 120px; margin-bottom: 0;">
            <label>Top K Search</label>
            <input type="number" name="top_k_search" value="{top_k_search}" min="1" max="50" required>
          </div>
          <div class="form-group" style="flex: 1; min-width: 120px; margin-bottom: 0;">
            <label>Top K Select</label>
            <input type="number" name="top_k_select" value="{top_k_select}" min="1" max="10" required>
          </div>
          <div class="form-group" style="flex: 1; min-width: 120px; margin-bottom: 0;">
            <label>Chunk Size</label>
            <input type="number" name="chunk_size" value="{chunk_size}" min="100" max="2000" required>
          </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.6); margin-bottom: 24px; display: flex; flex-wrap: wrap; gap: 20px; justify-content: space-between; align-items: center;">
          <div>
            <label style="font-size: 0.875rem; color: #64748b; margin-bottom: 12px; font-weight: 500; display: block;">Search Modes</label>
            <div class="checkbox-group">
              {''.join(mode_checkboxes)}
            </div>
          </div>
          <div>
            <label class="checkbox-label" style="background: #f8fafc; border-color: #cbd5e1;">
              <input type="checkbox" name="use_rerank" {rerank_checked}> 
              <span><svg style="vertical-align: middle; margin-right: 4px; margin-bottom: 2px;" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"></path></svg>Enable Reranker</span>
            </label>
          </div>
        </div>
        
        <button type="submit" class="btn-submit">
          <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          Execute Search
        </button>
      </form>
    </div>
    
    {results_html}
    
    {history_html}
  </div>

  <script>
    function showLoading() {{
      const button = document.querySelector('button[type="submit"]');
      button.style.pointerEvents = 'none';
      button.innerHTML = '<span style="display:inline-block; animation: spin 1s linear infinite; margin-right: 8px;">⏳</span> Processing...';
      document.getElementById('loading').style.display = 'flex';
    }}
  </script>
</body>
</html>"""


class ChatHandler(BaseHTTPRequestHandler):
    def send_session_cookie(self, session_id: str):
        self.send_header("Set-Cookie", f"{SESSION_COOKIE_NAME}={session_id}; Path=/; HttpOnly")

    def do_GET(self):
        session_id = get_session_id(self.headers)
        history = sessions.get(session_id, [])
        body = render_page(query="", selected_modes=DEFAULT_MODES, use_rerank=False, results=[], history=history, top_k_search=10, top_k_select=3, chunk_size=512)
        self.send_response(200)
        self.send_session_cookie(session_id)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_POST(self):
        session_id = get_session_id(self.headers)
        history = sessions.get(session_id, [])

        length = int(self.headers.get("Content-Length", 0))
        raw_data = self.rfile.read(length).decode("utf-8")
        params = parse_qs(raw_data)
        query = params.get("query", [""])[0].strip()
        selected_modes = params.get("mode", DEFAULT_MODES)
        use_rerank = "use_rerank" in params
        top_k_search = int(params.get("top_k_search", ["10"])[0])
        top_k_select = int(params.get("top_k_select", ["3"])[0])
        chunk_size = int(params.get("chunk_size", ["512"])[0])

        results = []
        if query:
            for mode in selected_modes:
                try:
                    response = rag_answer(
                        query,
                        retrieval_mode=mode,
                        top_k_search=top_k_search,
                        top_k_select=top_k_select,
                        use_rerank=use_rerank,
                        verbose=False,
                    )
                    response["mode"] = mode
                    results.append(response)
                except Exception as exp:
                    results.append({
                        "mode": mode,
                        "answer": f"Error: {html.escape(str(exp))}",
                        "sources": [],
                        "config": {"retrieval_mode": mode, "use_rerank": use_rerank},
                        "chunks_used": [],
                    })
            history.append({
                "query": query,
                "selected_modes": selected_modes,
                "use_rerank": use_rerank,
                "top_k_search": top_k_search,
                "top_k_select": top_k_select,
                "chunk_size": chunk_size,
                "results": results,
            })
            sessions[session_id] = history[-20:]

        body = render_page(query=query, selected_modes=selected_modes, use_rerank=use_rerank, results=results, history=history, top_k_search=top_k_search, top_k_select=top_k_select, chunk_size=chunk_size)
        self.send_response(200)
        self.send_session_cookie(session_id)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


def run_server(host: str = HOST, port: int = PORT):
    server = HTTPServer((host, port), ChatHandler)
    print(f"Web chatbot available at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
