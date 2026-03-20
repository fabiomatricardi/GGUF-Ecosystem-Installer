import os
import zipfile
import threading
import requests
import psutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class GGUFInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("GGUF Ecosystem Installer v1.1")
        self.root.geometry("720x610")
        
        self.project_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Status: Ready")
        self.progress_var = tk.DoubleVar(value=0)
        
        self.setup_ui()
        self.display_hardware_info()

    def setup_ui(self):
        # --- 1. Path Selection ---
        path_frame = tk.LabelFrame(self.root, text=" 1. Project Configuration ", padx=10, pady=10)
        path_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(path_frame, text="Select Install Folder:").pack(side="left")
        tk.Entry(path_frame, textvariable=self.project_path, width=50).pack(side="left", padx=5)
        tk.Button(path_frame, text="Browse", command=self.browse_folder).pack(side="left")

        # --- 2. Hardware Info ---
        hw_frame = tk.LabelFrame(self.root, text=" 2. System Overview ", padx=10, pady=10)
        hw_frame.pack(fill="x", padx=15, pady=10)
        
        self.hw_label = tk.Label(hw_frame, text="Detecting hardware...", justify="left")
        self.hw_label.pack(anchor="w")
        
        self.canvas = tk.Canvas(hw_frame, width=640, height=30, bg="#e0e0e0")
        self.canvas.pack(pady=5)

        # --- 3. Model Suggestions (Stacking Logic) ---
        self.model_frame = tk.LabelFrame(self.root, text=" 3. Recommended Models (GGUF) ", padx=10, pady=10)
        self.model_frame.pack(fill="x", padx=15, pady=10)
        
        # --- 4. Progress Section ---
        progress_frame = tk.Frame(self.root, padx=15)
        progress_frame.pack(fill="x", pady=10)
        
        self.prog_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.prog_bar.pack(fill="x")
        
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var, fg="blue")
        self.status_label.pack(pady=5)

        # --- 5. Controls ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.install_btn = tk.Button(btn_frame, text="Start Installation", command=self.start_install, 
                                     bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=20)
        self.install_btn.pack(side="left", padx=10)
        
        self.open_btn = tk.Button(btn_frame, text="Open Project Folder", command=self.open_folder, state="disabled")
        self.open_btn.pack(side="left", padx=10)

    def display_hardware_info(self):
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        avail_gb = mem.available / (1024**3)
        threads = psutil.cpu_count(logical=True)
        
        self.hw_label.config(text=f"Total RAM: {total_gb:.2f} GB | Available: {avail_gb:.2f} GB\nCPU Threads: {threads}")
        
        # Visual RAM Bar
        used_px = ((total_gb - avail_gb) / total_gb) * 640
        self.canvas.create_rectangle(0, 0, 640, 30, fill="#00FF00", outline="") # Free space
        self.canvas.create_rectangle(0, 0, used_px, 30, fill="#999999", outline="") # Used space
        
        self.suggest_models(total_gb)

    def suggest_models(self, ram_gb):
        for widget in self.model_frame.winfo_children():
            widget.destroy()

        # Model Definitions
        low_tier = [
            ("Qwen3.5-0.8B (Q4_K_M)", "https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF/resolve/main/Qwen3.5-0.8B-Q4_K_M.gguf?download=true"),
            ("Gemma-3-1B (Q4_K_M)", "https://huggingface.co/unsloth/gemma-3-1b-it-GGUF/resolve/main/gemma-3-1b-it-Q4_K_M.gguf?download=true")
        ]
        mid_tier = [
            ("Qwen3.5-2B (Q4_K_M)", "https://huggingface.co/unsloth/Qwen3.5-2B-GGUF/resolve/main/Qwen3.5-2B-Q4_K_M.gguf?download=true"),
            ("Llama-3.2-3B (Q4_K_M)", "https://huggingface.co/unsloth/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf?download=true")
        ]
        high_tier = [
            ("Gemma-3n-E2B (Q4_K_M)", "https://huggingface.co/unsloth/gemma-3n-E2B-it-GGUF/resolve/main/gemma-3n-E2B-it-Q4_K_M.gguf?download=true"),
            ("Qwen3-4B-Instruct (Q4_K_S)", "https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/resolve/main/Qwen3-4B-Instruct-2507-Q4_K_S.gguf?download=true")
        ]

        # Stacking Logic
        if ram_gb >= 12:
            tier_text = "High Capability (High + Mid + Low Tiers)"
            models = high_tier + mid_tier + low_tier
        elif ram_gb >= 9:
            tier_text = "Medium Capability (Mid + Low Tiers)"
            models = mid_tier + low_tier
        else:
            tier_text = "Low Capability (Low Tier)"
            models = low_tier

        tk.Label(self.model_frame, text=f"Tier: {tier_text}", font=("Arial", 9, "bold")).pack(anchor="w")
        
        btn_container = tk.Frame(self.model_frame)
        btn_container.pack(fill="x", pady=5)

        # Grid layout for multi-tier model buttons
        for i, (name, url) in enumerate(models):
            row, col = divmod(i, 2)
            tk.Button(btn_container, text=f"Download {name}", 
                      command=lambda u=url: self.download_model_standalone(u), 
                      width=30).grid(row=row, column=col, padx=5, pady=2)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path: self.project_path.set(path)

    def download_file(self, url, dest_folder, filename=None):
        if not filename:
            filename = url.split('/')[-1].split('?')[0]
        
        target_path = os.path.join(dest_folder, filename)
        
        if os.path.exists(target_path):
            self.status_var.set(f"Skipping {filename} (Exists)")
            return target_path

        self.status_var.set(f"Downloading {filename}...")
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        downloaded = 0
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        self.progress_var.set(percent)
                        self.root.update_idletasks()
        return target_path

    def start_install(self):
        path = self.project_path.get()
        if not path:
            return messagebox.showerror("Error", "Select an install folder.")
        
        self.install_btn.config(state="disabled")
        threading.Thread(target=self.run_installation_logic, daemon=True).start()

    def run_installation_logic(self):
        try:
            path = self.project_path.get()
            if not os.path.exists(path): os.makedirs(path)
            
            # 1. llama.cpp binaries
            zip_url = "https://github.com/ggml-org/llama.cpp/releases/download/b8429/llama-b8429-bin-win-cpu-x64.zip"
            zip_path = self.download_file(zip_url, path, "llama_binaries.zip")
            
            if zip_path.endswith(".zip"):
                self.status_var.set("Extracting binaries...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(path)
                os.remove(zip_path)

            # 2. Verify
            for exe in ["llama-cli.exe", "llama-server.exe"]:
                if not os.path.exists(os.path.join(path, exe)):
                    raise Exception(f"Missing {exe} after extraction.")

            # 3. Directories
            models_dir = os.path.join(path, "models")
            if not os.path.exists(models_dir): os.makedirs(models_dir)

            # 4. Applications
            apps = [
                ("https://github.com/fabiomatricardi/llamacppbenchmarks/releases/download/GGUFbatchBenchmarking/GGUF_batch_Benchmark.exe", "GGUF_batch_Benchmark.exe"),
                ("https://github.com/fabiomatricardi/tkinter-llamaCLI-speedTest/releases/download/tk-llamacpp-test/GGUF_Bench_v1.6.5.exe", "GGUF_Bench_v1.6.5.exe"),
                ("https://github.com/fabiomatricardi/llama-server-runner/releases/download/GGUFrunner/GGUF-server-runner_v1.0.exe", "GGUF-server-runner_v1.0.exe")
            ]
            
            for url, name in apps:
                self.download_file(url, path, name)

            self.status_var.set("Success!")
            self.progress_var.set(100)
            self.open_btn.config(state="normal")
            messagebox.showinfo("Success", "Installation complete!")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.install_btn.config(state="normal")

    def download_model_standalone(self, url):
        path = self.project_path.get()
        if not path: return messagebox.showwarning("Warning", "Set path first.")
        
        models_dir = os.path.join(path, "models")
        if not os.path.exists(models_dir): os.makedirs(models_dir)
        
        threading.Thread(target=lambda: self.download_file(url, models_dir), daemon=True).start()

    def open_folder(self):
        os.startfile(self.project_path.get())

if __name__ == "__main__":
    root = tk.Tk()
    app = GGUFInstaller(root)
    root.mainloop()