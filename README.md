# 🚀 GGUF Ecosystem Installer

An all-in-one automation tool designed to turn any Windows PC into a local LLM powerhouse. This installer detects your hardware, sets up the latest `llama.cpp` binaries, and provides a curated selection of optimized GGUF models based on your available System RAM.

<img width="722" height="642" alt="ggufinstaller001" src="https://github.com/user-attachments/assets/acd66bd5-8341-422e-bafa-0f779b90cbfa" />

## Windows executable
You can find the pre-compiled [windows binaries (GGUF-ecosystem-installer.exe) here](https://github.com/fabiomatricardi/GGUF-Ecosystem-Installer/releases/tag/GGUF_Ecosystem_Installer)

---

## 🌟 Key Features

* **Hardware-Aware Recommendations**: Automatically categorizes your PC into Low, Medium, or High tiers and suggests compatible models.
* **Complete Toolchain Setup**: Downloads and configures:
* `llama-cli.exe` & `llama-server.exe` (Official llama.cpp binaries).
* **GGUF Server Runner**: An API/Web UI launcher.
* **GGUF Benchmarking & Inspection Tool**: For performance testing ($t/s$).
* **CLI Batch Benchmarking**: For automated testing.


* **Smart Downloads**: Features a per-file progress bar and skips existing files to save bandwidth.
* **No-GPU Required**: Optimized specifically for GGUF formats to ensure high performance even on CPU-only systems.

---

## 🛠️ Installation & Usage

1. **Prerequisites**: Ensure you have [Python 3.x](https://www.python.org/downloads/) installed.
2. **Dependencies**: Install the required system monitoring library:
```bash
pip install psutil requests

```


3. **Run the Installer**:
```bash
python GGUF_ecosystem_installer.py

```
<img width="722" height="642" alt="ggufinstaller003" src="https://github.com/user-attachments/assets/750d4e9b-f4a7-4619-8b51-ef1fc58206b4" />

<img width="722" height="642" alt="ggufinstaller002" src="https://github.com/user-attachments/assets/52cf20b9-e673-4f10-91a1-4fad0ceb3427" />

4. **Setup**:
* Select your desired project folder.
* Click **"Start Installation"** to fetch binaries and tools.
* Choose from the recommended models to begin your AI journey.



---

## 📖 Code Explanation

The installer is built using Python's `tkinter` for the GUI and several powerful libraries for system interaction.

### 1. Hardware Detection (`psutil`)

The script uses `psutil.virtual_memory()` to grab the total and available RAM. This is critical for GGUF inference, where the entire model must ideally fit into RAM to avoid slow disk swapping.

```python
mem = psutil.virtual_memory()
total_gb = mem.total / (1024**3)

```

### 2. Multi-Tier Stacking Logic

Unlike simple "if/else" logic, this script uses **Capability Stacking**. If a user has a High-Tier PC, they are shown the most powerful models *plus* the lighter models from lower tiers for maximum flexibility.

```python
if ram_gb >= 12:
    models = high_tier + mid_tier + low_tier # High-tier users see everything

```

### 3. Threaded Downloads (`threading` & `requests`)

To prevent the GUI from freezing during large 2GB+ downloads, the installation logic runs on a background thread. The `requests` library streams the file in chunks, calculating the percentage for the `ttk.Progressbar` in real-time.

```python
with open(target_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        # Update progress bar calculations here

```

### 4. Binary Management (`zipfile`)

The official `llama.cpp` releases come as ZIP files. The installer automatically extracts these, verifies the existence of the `.exe` files, and cleans up the temporary ZIP to keep your workspace tidy.

---

## 📂 Project Structure Created

After running the installer, your folder will look like this:

```text
Your-Project-Folder/
├── models/                  # GGUF models (.gguf)
├── llama-cli.exe            # Core inference engine
├── llama-server.exe         # Local API server
├── GGUF-server-runner.exe   # GUI for server management
├── GGUF_Bench_v1.6.5.exe    # Performance tester
└── libllama.dll             # Required library

```

