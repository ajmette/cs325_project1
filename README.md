Downloading/ setting up phi3:
    downloaded from https://ollama.com/
    after some trouble shooting (uninstalling ollama, reinstalling ollama, and restarting computer), notification popped up to finish set up
    ran "ollama run phi3" in command prompt
    used "pip install ollama-python" in command prompt to interact with python
    ran "ollama pull llama3.1"

program.py file:
    reads given ollama prompts from prompts.txt file
    does ollama phi3 chat with each prompt
    records ollama answers into answers.txt file