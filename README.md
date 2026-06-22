# Intialisation

## create a virtual environment and activate it

Windows\
python -m venv .venv\
.venv\Scripts\activate\

## Install requirements

pip install -r requirements.txt\

# Run
python main.py\
Install Ollama from https://ollama.com/download\
Open the Ollama app, or make sure the local Ollama server is running at http://localhost:11434\
Open new terminal\
Download the model:ollama pull gemma3\
ollama serve\
ollama run gemma3\


## Current code functionality
main.py is the current code entry point. \Calls voskMain which prompts user to speak and records input. \Press Ctrl + C to end recording. \Outputs to transcript.csv
\ ollamaMain is called and the csv file is then passed to Ollama which corrects the grammar and saves to corrected_sentence column \

# Development instructions

Please create your own development branch for the feature you are working on. \If there is a pre existing branch for the feature use that one. When your fuctions are ready, \create a pull request to be reviewed by another team member.\ It will be merged with the main branch and you can make a \development branch again for the next feature.

You should make your own file for the functions you are making and then import the\ functions to main to call when needed. Please call your file something relevent to the functions and name the functions in\ a way that is obvious what they do.

git --no-pager log > gitLog.txt