import os
import subprocess
import sys
from pathlib import Path

import tkinter as tk
from tkinter import scrolledtext

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent

# ================= UI =================
class VoiceLegalUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Legal Voice Assistant")
        self.root.geometry("880x620")
        self.root.configure(bg="#0f172a")
        self.processes = {}

        title = tk.Label(
            root,
            text="Legal Voice Assistant",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#0f172a"
        )
        title.pack(pady=(16, 8))

        sub = tk.Label(
            root,
            text="Speak your issue. The assistant runs in the background.",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#0f172a"
        )
        sub.pack(pady=(0, 12))

        self.chat = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            width=100,
            height=24,
            font=("Consolas", 11),
            bg="#0b1220",
            fg="#e2e8f0"
        )
        self.chat.pack(padx=16, pady=8, fill=tk.BOTH, expand=True)

        controls = tk.Frame(root, bg="#0f172a")
        controls.pack(pady=(0, 10))

        self.start_main_btn = tk.Button(
            controls,
            text="Start Assistant",
            command=self.start_main_assistant,
            width=18,
            bg="#22c55e",
            fg="white",
            font=("Segoe UI", 10, "bold")
        )
        self.start_main_btn.grid(row=0, column=0, padx=8)

        self.stop_main_btn = tk.Button(
            controls,
            text="Stop Assistant",
            command=self.stop_main_assistant,
            width=18,
            bg="#ef4444",
            fg="white",
            font=("Segoe UI", 10, "bold")
        )
        self.stop_main_btn.grid(row=0, column=1, padx=8)

        self.status = tk.Label(
            root,
            text="Ready",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#0f172a"
        )
        self.status.pack(pady=(0, 10))

        launcher = tk.Frame(root, bg="#0f172a")
        launcher.pack(pady=(0, 16))

        tk.Label(
            launcher,
            text="Tools",
            font=("Segoe UI", 11, "bold"),
            fg="#e2e8f0",
            bg="#0f172a"
        ).grid(row=0, column=0, columnspan=4, pady=(0, 6))

        self._add_tool_button(launcher, "Voice RAG", "voice_rag_assistant.py", 1, 0)
        self._add_tool_button(launcher, "Voice Input", "voice_input.py", 1, 1)
        self._add_tool_button(launcher, "Load Data", "load_data.py", 1, 2)
        self._add_tool_button(launcher, "Vector Store", "vector_store.py", 1, 3)
        self._add_tool_button(launcher, "Chunking", "chunking.py", 2, 0)
        self._add_tool_button(launcher, "Query Search", "query_search.py", 2, 1)
        self._add_tool_button(launcher, "Generate Answer", "generate_answer.py", 2, 2)

        greeting = "Hello, I am Deak. How can I assist you?"
        self._append_chat("Assistant", greeting)
        self.root.after(300, self.start_main_assistant)

    def _add_tool_button(self, parent: tk.Frame, label: str, script: str, row: int, col: int) -> None:
        btn = tk.Button(
            parent,
            text=label,
            command=lambda s=script: self._run_script(s),
            width=16,
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 9, "bold")
        )
        btn.grid(row=row, column=col, padx=6, pady=4)

    def _run_script(self, script_name: str) -> None:
        script_path = BASE_DIR / script_name
        if not script_path.exists():
            self._append_chat("System", f"Missing: {script_name}")
            return

        creation_flags = 0
        if os.name == "nt" and hasattr(subprocess, "CREATE_NEW_CONSOLE"):
            creation_flags = subprocess.CREATE_NEW_CONSOLE

        try:
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(BASE_DIR),
                creationflags=creation_flags
            )
            self.processes[script_name] = process
            self._append_chat("System", f"Started: {script_name}")
        except Exception as exc:
            self._append_chat("System", f"Failed to start {script_name}: {exc}")

    def start_main_assistant(self) -> None:
        self.status.config(text="Assistant running")
        if self._is_running("voice_rag_assistant.py"):
            return
        self._run_script("voice_rag_assistant.py")

    def stop_main_assistant(self) -> None:
        self.status.config(text="Assistant stopped")
        self._stop_script("voice_rag_assistant.py")

    def _is_running(self, script_name: str) -> bool:
        proc = self.processes.get(script_name)
        return proc is not None and proc.poll() is None

    def _stop_script(self, script_name: str) -> None:
        proc = self.processes.get(script_name)
        if proc is None:
            return
        try:
            proc.terminate()
            self._append_chat("System", f"Stopped: {script_name}")
        except Exception as exc:
            self._append_chat("System", f"Failed to stop {script_name}: {exc}")

    def _append_chat(self, role: str, text: str) -> None:
        self.chat.insert(tk.END, f"{role}: {text}\n\n")
        self.chat.see(tk.END)


def on_close(root: tk.Tk) -> None:
    root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceLegalUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
    root.mainloop()
