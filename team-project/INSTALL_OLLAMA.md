# Installing Ollama Locally

Use this guide if your team chooses Ollama instead of Gemini.

The provided example file is:

```text
examples/ollama_correct_example.py
```

It uses:

```python
MODEL_NAME = "gemma3"
OLLAMA_URL = "http://localhost:11434/api/generate"
```

## 1. Install Ollama

Install Ollama from the official download page:

[https://ollama.com/download](https://ollama.com/download)

Use the version for your operating system:

- macOS: install the app and open it.
- Windows: install the app and open it.
- Linux: follow the install command shown on the download page.

## 2. Check That Ollama Works

Open a terminal and run:

```bash
ollama --version
```

If this prints a version number, Ollama is installed.

## 3. Download the Model

The example uses `gemma3`, so download that model:

```bash
ollama pull gemma3
```

If your computer is slow or has limited memory, use the smaller model:

```bash
ollama pull gemma3:1b
```

If you use `gemma3:1b`, also change this line in
`examples/ollama_correct_example.py`:

```python
MODEL_NAME = "gemma3:1b"
```

## 4. Make Sure Ollama Is Running

Ollama runs a local server on:

```text
http://localhost:11434
```

The example sends requests to:

```text
http://localhost:11434/api/generate
```

Test the local server with:

```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "gemma3", "prompt": "Correct this: can we target students first", "stream": false}'
```

If you get a response, the local server is working.

## 5. Run the Python Example

From the project folder, run:

```bash
python3 examples/ollama_correct_example.py
```

## Common Problem

If Python shows a connection error, Ollama is probably not running or is not
available at `localhost:11434`.

Fix:

1. Open the Ollama app again.
2. Run `ollama --version`.
3. Retry the `curl` test.
4. Run the Python example again.
