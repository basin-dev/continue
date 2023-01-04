# rm completions_prepared.jsonl
openai tools fine_tunes.prepare_data -f docstring_completions.json
openai api fine_tunes.create -t docstring_completions_prepared.jsonl -m davinci --suffix "docstring_completions_davinci_1"