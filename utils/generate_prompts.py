from pathlib import Path

from test_prompt_generator.test_prompt_generator import _preset_tokenizers, generate_prompt

files_root = Path(__file__).parents[1] / "test_prompt_generator/text_files"
source_files = {"en": files_root / "alice.txt", "zh": files_root / "watermargin.txt"}


def generate_all_prompts(prompts_dir):
    """
    Utility function to generate prompts for different input sizes for all preset tokenizers.
    Prompts are saved in prompt_dir/tokenizer_dir/prompt_{num_tokens}.jsonl
    """
    for lang, source_file in source_files.items():
        for tokenizer in _preset_tokenizers:
            print(tokenizer, lang)
            for num_tokens in (32, 64, 128, 256, 512, 1024, 2048, 3072, 4000, 4096):
                for output_type in ("jsonl", "txt"):
                    if not (tokenizer == "t5" and num_tokens > 2048):
                        if not (lang == "zh" and tokenizer in ("bert", "t5", "blenderbot")):
                            generate_prompt(
                                tokenizer_id=tokenizer,
                                num_tokens=num_tokens,
                                prefix="Summarize this text:" if lang == "en" else "总结这篇课文：",
                                output_file=prompts_dir / lang / output_type / Path(tokenizer) / f"prompt_{num_tokens}.{output_type}",
                                overwrite=True,
                                source_text_file=source_file,
                            )


if __name__ == "__main__":
    prompts_dir = Path(__file__).parents[1] / "prompts"
    print(prompts_dir)
    generate_all_prompts(prompts_dir)
