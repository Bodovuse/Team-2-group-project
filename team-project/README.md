# Team Project Brief: Meeting Speech Analytics with Vosk + AI

## 1. Project goal

Your team will build a data analytics pipeline for a startup that builds a
team meeting application.

The pipeline should:

1. Record short spoken statements from different team members.
2. Transcribe the speech with an audio model, such as Vosk.
3. Correct the transcript with an AI option, for example Gemini API, local Ollama, or another model.
4. Save the results in a CSV dataset.
5. Enrich your data with Python.
6. Validate the dataset before analysis.
7. Produce basic speaking analytics.

The final project should be clear enough that anyone can clone your
repository, install the dependencies, run the code, and understand the output.

## 2. Scenario

Imagine your team is having a short startup meeting. Each person says one or
more short phrases that are transcribed by an audio model. For example:

- Stelios: "hello team today we discuss mobile app growth"
- Mary: "can we target students first"
- Kate: "i think we need lower pricing for early users"

For this project, you can use Vosk, which transcribes audio but may produce imperfect text. Your job is to keep the raw Vosk transcript, correct it with AI, and then analyze the cleaned data.

Minimum dataset size:

- At least 25 rows in your final CSV.
- Rows should come from your own team recordings, not only from the examples in
  this brief.

## 3. Recommended technologies

Use:

- Python
- Vosk speech recognition
- Vosk model: `vosk-model-en-us-0.22-lgraph` (128M)
- Gemini API or local Ollama for transcript correction
- CSV files for storing the dataset

Download the Vosk model from: [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)

After downloading, unzip it so your project contains a folder like this:

```text
vosk-model-en-us-0.22-lgraph/
```

> Explore the example code for how to use the model. You may use any model or Python library that you prefer, as long as you can explain its time and space complexity.

## 4. Starter files

This folder contains examples to help you start. They are not a complete final submission.

| File | Purpose |
| --- | --- |
| `examples/vosk_microphone_black_box.py` | A small microphone transcription example using Vosk. Students must adapt it for speaker names, timing, and CSV output. |
| `examples/gemini_correct_example.py` | Shows how to send one transcript to Gemini and print the corrected sentence. |
| `examples/ollama_correct_example.py` | Shows how to send one transcript to a local Ollama model and print the corrected sentence. |
| `requirements.txt` | Python packages used by the examples. |
| `Peer_Evaluation_Form.docx` | Individual peer evaluation form. Each student submits this separately. |

## 5. Pipeline requirements

Your project should implement these stages.

### Stage 1: Record and transcribe speech

Record each speaker turn and save a raw CSV row. Example raw data:

| timestamp | name | raw_text_vosk | time_taken_sec |
| --- | --- | --- | --- |
| `2026-04-28T10:00:05` | Stelios | `helo team today we discuss mobile app growth` | `6.2` |
| `2026-04-28T10:00:18` | Mary | `can we target students first` | `3.8` |
| `2026-04-28T10:00:30` | Kate | `i think we need lower pricing for early users` | `5.1` |

### Stage 2: Correct the Transcript With AI

Send each `raw_text_vosk` value to Gemini or Ollama. The AI should correct spelling, punctuation, and readability. It should not change the meaning. For example, you can add a new column.

| Column | Meaning |
| --- | --- |
| `text` | AI-corrected version of `raw_text_vosk` |

Example corrected data:

| timestamp | name | raw_text_vosk | text | time_taken_sec |
| --- | --- | --- | --- | --- |
| `2026-04-28T10:00:05` | Stelios | `helo team today we discuss mobile app growth` | `Hello team, today we discuss mobile app growth.` | `6.2` |
| `2026-04-28T10:00:18` | Mary | `can we target students first` | `Can we target students first?` | `3.8` |
| `2026-04-28T10:00:30` | Kate | `i think we need lower pricing for early users` | `I think we need lower pricing for early users.` | `5.1` |

### Stage 3: Enrich the Dataset With Python

Use Python logic, not AI, to add calculated columns. Recommended final columns:

| Column | How to calculate it |
| --- | --- |
| `timestamp` | Keep from the raw data. |
| `name` | Keep from the raw data. |
| `raw_text_vosk` | Keep from the raw data. |
| `text` | AI-corrected transcript. |
| `time_taken_sec` | Keep from the raw data. |
| `question_flag` | `True` if `text` ends with `?`, otherwise `False`. |
| `num_words` | Number of words in `text`. |
| `text_size_chars` | Number of characters in `text`. |
| `speech_rate_wps` | `num_words / time_taken_sec`, rounded sensibly. |
| `speaker_turn_id` | Running count for each speaker: first turn is 1, second turn is 2, etc. |

Example enriched data:

| timestamp | name | text | time_taken_sec | question_flag | num_words | text_size_chars | speech_rate_wps | speaker_turn_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2026-04-28T10:00:05` | Stelios | `Hello team, today we discuss mobile app growth.` | `6.2` | `False` | `8` | `47` | `1.29` | `1` |
| `2026-04-28T10:00:18` | Mary | `Can we target students first?` | `3.8` | `True` | `5` | `29` | `1.32` | `1` |
| `2026-04-28T10:00:30` | Kate | `I think we need lower pricing for early users.` | `5.1` | `False` | `9` | `46` | `1.76` | `1` |
| `2026-04-28T10:00:40` | Stelios | `Ok, let's proceed!` | `3.2` | `False` | `3` | `18` | `0.94` | `2` |

### Stage 4: Validate the CSV

Before analytics, your code should check that the final CSV is usable (the CSV has at least 25 rows).

At minimum, check:

- No required values are missing.
- `timestamp` values can be parsed as dates/times.
- `time_taken_sec` is numeric and greater than 0.
- `num_words` is numeric and greater than 0.
- `speech_rate_wps` is numeric and greater than 0.
- `question_flag` contains boolean values.
- `speaker_turn_id` is numeric and greater than 0.

Validation should print clear messages. For example:

```text
Validation failed:
- Row 4: timestamp "-04-28T10:00:05" is not a valid datetime.
- Row 3: speech_rate_wps is missing.
```

### Stage 5: Analyse the Dataset

After validation passes, answer these questions:

1. Who spoke the most by total words?
2. Who spoke the least by total words?
3. What is the total speaking time of the meeting?
4. What is the average speaking time per speaker?
5. Who asked the most questions?
6. Who are the top 5 speakers by total speaking time?
7. What is each speaker's average speech rate?

Use clear output. Console output is acceptable. A short report is also acceptable. The following is an example analytics output for the four valid rows above. Feel free to improvise if you find a better format.

| Metric | Result |
| --- | --- |
| Most words | Stelios, 11 words |
| Least words | Mary, 5 words |
| Total speaking time | 18.3 seconds |
| Average speaking time per speaker | 6.1 seconds |
| Most questions | Mary, 1 question |
| 1st speaker by time | Stelios, 9.4 seconds |
| 2nd speaker by time | Kate, 5.1 seconds |
| 3rd speaker by time | Mary, 3.8 seconds |
| Stelios average speech rate | 1.17 words/second |
| Mary average speech rate | 1.32 words/second |
| Kate average speech rate | 1.76 words/second |

## 8. Complexity Discussion

Include a short README explaining time and space complexity. You should explain the major operations in your code.

## 9. Deliverables

Submit:

1. A GitHub repository with runnable code.
2. A final CSV dataset with at least 25 rows.
3. Validation output, either in the console, a log file, or a short report.
4. Analytics output, either in the console or a short report.
5. A short project README explaining:
   - what the app does,
   - how to install dependencies,
   - how to run the project,
   - what files are produced.
6. A team presentation video.
7. An individual peer evaluation form from each team member.

Share your team repository with Stelios on GitHub. The GitHub handle is: `steliosot`.

## 10. Video Guidance

Keep the video simple and focused. Recommended structure:

1. Briefly introduce the project.
2. Show the tool running from a user point of view.
3. Show the CSV output.
4. Show the validation and analytics output.
5. Each team member briefly explains what they worked on.

You do not need to explain the code.

## 11. Peer Evaluation

Each student must submit `Peer_Evaluation_Form.docx` individually.

- Do not mark yourself.
- Give each teammate a score from 0 to 100.
- Add comments where useful.
- The peer evaluation form is required. Without it, the submission cannot be accepted.


## 12. Use of AI

You may use AI tools to help debug code, understand errors, and improve your workflow. You may also use AI for transcript correction. However:

- You must understand your final code.
- You must be able to explain your final submission.
- You must not submit code that your team cannot run or explain.

## 13. Optional Extensions

These are optional (not graded).

- Sentiment analysis per speaker.
- Charts showing speaking time or word count per speaker.

## 14. Evaluation Checklist

Use this before submission:

- [ ] GitHub repository is shared with `steliosot`.
- [ ] Code runs from clear instructions.
- [ ] Vosk model is used correctly.
- [ ] Gemini or Ollama correction is implemented (other models are also acceptable).
- [ ] Final CSV has at least 25 rows.
- [ ] Final CSV includes all required columns.
- [ ] Validation checks are implemented.
- [ ] Analytics questions are answered.
- [ ] Time and space complexity are explained.
- [ ] README is clear and short.
- [ ] Team video is recorded and shared.
- [ ] Each student submits the peer evaluation form individually.

## 15. Rubric

The final mark has two parts:

- 50% from peer evaluation.
- 50% from Stelios.

The rubric below is used for Stelios's 50%.

| Area | Weight | What We Are Looking For |
| --- | --- | --- |
| Speech-to-text pipeline | 20% | Correct use of Vosk and the required model; clear raw transcript output. |
| AI correction | 15% | Sensible use of Gemini or Ollama; corrected text keeps the original meaning. |
| CSV dataset and enrichment | 20% | At least 25 rows; required columns; Python-generated features are correct. |
| Validation and analytics | 20% | Useful validation checks; correct statistics; sorted top-5 speaker output. |
| Team collaboration and GitHub | 10% | Clear repository structure; evidence of shared work; readable commits or branches. |
| README, presentation, and explanation | 15% | Clear run instructions; working demo; time and space complexity explained. |

## 16. Need Advice?

Book a call with Stelios to chat about your project with your team: [https://cal.com/steliosot/15min](https://cal.com/steliosot/15min)
