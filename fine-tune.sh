rm completions_prepared.jsonl
openai tools fine_tunes.prepare_data -f completions.json
openai api fine_tunes.create -t completions_prepared.jsonl -m curie