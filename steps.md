# SkyV - Windows Setup Guide

A fully offline voice dictation app for Windows. Press `Ctrl+Shift` to start recording, speak, press again to paste cleaned text anywhere. Built from the macOS version and adapted for Windows.

---

## Prerequisites

### 1. Install Python 3.12
- Download from: https://www.python.org/downloads/
- **IMPORTANT**: Check "Add Python to PATH" during installation
- Verify: `python --version`

### 2. Install Ollama (for LLM text cleanup - optional but recommended)
- Download from: https://ollama.com/download/windows
- Install and launch Ollama
- Pull a model: `ollama pull llama3.2:3b` (or `qwen2.5:1.5b` for slower PCs)

---

## Setup


### 1. Clone or download the project
```bash
git clone https://github.com/anesriad/VoiceBud-Local-Riad.git
cd VoiceBud-Local-Riad