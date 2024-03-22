# Prompts

Pre-created prompts for popular model architectures, in .jsonl format. The following preset tokenizers were used to create these prompts:

| preset   | model_id                             |
| :------- | :----------------------------------- |
| bert     | google-bert/bert-base-uncased        |
| bloom    | bigscience/bloom-560m                |
| chatglm3 | THUDM/chatglm3-6b                    |
| falcon   | tiiuae/falcon-7b                     |
| gemma    | fxmarty/tiny-random-GemmaForCausalLM |
| gpt-neox | EleutherAI/gpt-neox-20b              |
| llama    | TinyLlama/TinyLlama-1.1B-Chat-v0.6   |
| mistral  | mistralai/Mistral-7B-v0.1            |
| opt      | facebook/opt-2.7b                    |
| phi-2    | microsoft/phi-2                      |
| pythia   | EleutherAI/pythia-1.4b-deduped       |
| qwen     | Qwen/Qwen1.5-7B-Chat                 |
| roberta  | FacebookAI/roberta-base              |
| t5       | google-t5/t5-base                    |

The jsonl files have the following structure:

```json
{
  "prompt": "Alice was beginning to get very tired of sitting by her sister on the bank,",
  "model_id": "tiiuae/falcon-7b",
  "num_tokens": 16
}
```
