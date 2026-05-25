# Team Project Clarification 06/05/2026

This note adds practical guidance for the team project. It does not replace the main assignment brief.

## 1. What is Vosk?

Vosk is an offline speech-to-text toolkit. In this project, you can use it to listen to a short audio recording or microphone input and produce a text transcript. 

Vosk does not automatically know who is speaking. Your team must still record or type the speaker name yourselves.

## 2. How to record your data

Sit together as a team and record short turns.

For each turn:

1. One student says their name clearly and loudly.
2. The same student says one short meeting phrase.
3. Save the name using your Python magic in your CSV.
4. Use Vosk to transcribe the spoken phrase.

Example:

```text
Name: Maria
Phrase: I think we should test the app with students first
```

Your CSV might store this as:

```csv
timestamp,name,raw_text_vosk,time_taken_sec
2026-05-06T14:10:00,Maria,i think we should test the app with students first,5.2
```

## 3. You can start with a synthetic CSV

If the recording stage blocks you at the beginning, create a small synthetic CSV first so you can build the rest of the pipeline.

For example, you can create fake rows with:

- `timestamp`
- `name`
- `raw_text_vosk`
- `time_taken_sec`

Then build the correction, enrichment, validation, and analytics stages around
that CSV. Later, replace the synthetic rows with real team recordings.

## 4. Work in small stages

Treat each stage as a small task:

1. Record or create raw rows.
2. Save raw rows to CSV.
3. Correct the transcript with AI.
4. Add calculated columns with Python.
5. Validate the final CSV.
6. Run the analytics.
7. Write a short explanation of the complexity.

Document each stage so the project is reproducible. Someone else should be able to clone your repository, install dependencies, and run your code.

Keep `requirements.txt` updated whenever you add a new Python package.

## 5. GitHub and team workflow

Use one private GitHub repository shared by all team members.

You can also share the repository with Stelios if you want feedback. GitHub: `steliosot`.

As a team, spend 10-15 minutes learning how pull requests work. Pull requests are good practice because they help you review each other's changes before merging code.

Suggested video:

[How to create a pull request on GitHub](https://www.youtube.com/watch?v=nCKdihvneS0&t)

## 6. Book a team call

If your team has questions, book a short call with Stelios as a team:

[https://cal.com/steliosot/15min](https://cal.com/steliosot/15min)

Come with specific questions, for example:

- Which part of our pipeline should we build first?
- Is our CSV structure sensible?
- Are we using AI correctly?
- How should we explain complexity?

## 7. Feel free to improvise

You may improve the project if you can explain what you changed and why.

For example, you can:

- Try a better speech-to-text model than Vosk.
- Use Gemini, GPT, Ollama, or another AI tool for transcript correction.
- Add charts or extra analytics.
- Improve the CSV structure.
- Compare two approaches and explain the trade-off.

The important rule is that your team must understand the code and be able to
explain the final project.

## 8. Use AI, but learn the workflow

Use AI to help you:

- break the project into tasks,
- debug errors,
- understand Python code,
- write cleaner documentation,
- learn Git commands such as pull, push, branch, and pull request.

Do not use AI only to produce a final answer. Use it to learn how the project works, so every team member can explain their contribution.
