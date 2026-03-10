# Pandas-AI

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-black)
![License](https://img.shields.io/badge/License-MIT-green)
![Local AI](https://img.shields.io/badge/AI-Local%20LLM-orange)

Pandas-AI is a **local AI-powered academic rewriting assistant** designed for thesis, research papers, and academic writing.

It uses **Flask + Local LLM (Ollama)** to rewrite text in a more **formal, clear, and academic ready style**.

---

## Features

- Academic thesis/research-style rewriting
- Grammar suggestions
- Readability analysis
- Writing quality insights
- Clean web interface
- Runs completely **locally**

## Future Improvements

- Add support for multiple LLM models
- Improve rewriting speed and optimization
- Add citation and reference assistance
- Provide REST API access

---

## Tech Stack

- Python
- Flask
- Ollama (Local LLM)
- HTML / CSS / JavaScript
- NLP tools

---

## Installation

Clone the repository:

git clone https://github.com/durjoyds-7/Pandas-AI

cd Pandas-AI

Install dependencies:

pip install -r requirements.txt


## Install Ollama Model

Download Ollama:
https://ollama.com

Start Ollama:

ollama serve

Pull the model:

ollama pull llama3


## Run the App

python app.py

---

## How to Use

1. Paste your text in the input box
2. Select rewrite mode
3. Click rewrite
4. The AI will generate an academic version

## Example

Input:

This research study was conducted to examine the impact of social media on student learning behavior.

Output:

This study investigates the impact of social media on students' learning behavior.

---

## Project Structure

Pandas-AI/
│
├── app.py                # Flask application
├── requirements.txt      # Python dependencies
├── ai_engine/            # AI modules
│   ├── llm_rewrite.py
│   ├── grammar.py
│   ├── readability.py
│   └── quality.py
│
├── humanizer/            # text preprocessing
│
├── templates/            # HTML templates
├── static/               # CSS / JS
│
└── screenshots/          # demo images

---

## screenshots

![App interface](screenshot/home.png)

![App interface](screenshot/home2.png)

---

## Why this project?

Pandas-AI helps improve academic writing by combining:

- Local LLM rewriting
- Grammar analysis
- Readability scoring
- Clarity and redundancy detection
