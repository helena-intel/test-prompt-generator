import json
import re
import warnings
from pathlib import Path

from transformers import AutoTokenizer


def generate_prompt(model_id, length, output_file=None, silent=False, source_text_file=None):
    if source_text_file is None:
        source_text_file = Path(__file__).parent / "text_files" / "alice.txt"
    if not silent:
        print(f"Generating prompts from {source_text_file}")
    source_text = Path(source_text_file).read_text()
    # Some tokenizers treat "\n\n" at the end of a sentence differently than in the middle;
    # replace consecutive "\n" with 1 to prevent generating an incorrect number of tokens
    source_text = re.sub(r"\n+", "\n", source_text)

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    # prevent warnings about too many tokens from tokenizing the entire source text
    tokenizer.model_max_length = 10000
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="^.*Token indices.*$")

        inputs = tokenizer(source_text)

    tokens = inputs["input_ids"]
    total_tokens = len(tokens)
    prompt = None
    if length > total_tokens:
        raise ValueError(
            f"""Cannot generate prompt with {length} tokens because the source text contains {total_tokens} tokens.
            Please edit the source text file to create longer prompts"""
        )

    prompt = tokenizer.decode(tokens[:length], skip_special_tokens=True)
    prompt_tokens = tokenizer(prompt)
    if len(prompt_tokens["input_ids"]) != length:
        print("prompt", repr(prompt))
        print("prompt_tokens", prompt_tokens["input_ids"])
        print("source_tokens", tokens[:length])
        raise RuntimeError(f"Expected {length} tokens, got {len(prompt_tokens['input_ids'])}")

    if tokenizer.decode(prompt_tokens["input_ids"][1:]) != prompt:
        print("prompt", prompt)
        print("decoded prompt", tokenizer.decode(prompt_tokens["input_ids"][1:]))
        raise RuntimeError("prompts don't match")

    if output_file is not None:
        prompt_dict = {"prompt": prompt}
        with open(output_file, "w") as f:
            json.dump(prompt_dict, f, ensure_ascii=False)

    if not silent:
        print(prompt)
        print(list(tokens[:length]))

    if prompt is None:
        raise RuntimeError(f"Generating prompt with {length} tokens failed")

    return prompt


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tokenizer",
        required=True,
        help="model_id from Hugging Face hub, or path to local directory with tokenizer files",
    )
    parser.add_argument("-n", "--num_tokens", required=True, type=int, help="Number of tokens the generated prompt should have")
    parser.add_argument("-o", "--output_file", required=False, help="Path to file to store the prompt as .jsonl file")
    parser.add_argument("-s", "--silent", action="store_true")
    parser.add_argument(
        "-f", "--file", required=False, help="Optional: path to text file to generate prompts from. Default text_files/alice.txt"
    )
    args = parser.parse_args()

    generate_prompt(args.tokenizer, args.num_tokens, args.output_file, args.silent, args.file)
