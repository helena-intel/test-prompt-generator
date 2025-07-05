from test_prompt_generator.test_prompt_generator import _preset_tokenizers, generate_prompt
from pathlib import Path


def generate_all_prompts(prompts_dir):
    """
    Utility function to generate prompts for different input sizes for all preset tokenizers.
    Prompts are saved in prompt_dir/tokenizer_dir/prompt_{num_tokens}.jsonl
    """
    for tokenizer in _preset_tokenizers:
        print(tokenizer)
        for num_tokens in (16, 32, 64, 128, 256, 512, 1024, 2048, 3072, 4000, 4098):
            for output_type in ("jsonl", "txt"):
                generate_prompt(
                    tokenizer_id=tokenizer,
                    num_tokens=num_tokens,
                    prefix="Summarize this text:",
                    output_file=prompts_dir / output_type / Path(tokenizer) / f"prompt_{num_tokens}.{output_type}",
                    overwrite=True,
                )


if __name__ == "__main__":
    prompts_dir = Path(__file__).parents[1] / "prompts"
    print(prompts_dir)
    generate_all_prompts(prompts_dir)
