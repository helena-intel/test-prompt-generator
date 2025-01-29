import json
import subprocess
import tempfile
from pathlib import Path

import pytest
from transformers import AutoTokenizer

from test_prompt_generator import generate_prompt
from test_prompt_generator.test_prompt_generator import _preset_tokenizers

prompts_root = Path(__file__).parents[1] / "prompts"
prompt_dirs = [p for p in prompts_root.iterdir() if p.is_dir()]

sample_text = """Emma Woodhouse, handsome, clever, and rich, with a comfortable home and happy disposition, seemed to
unite some of the best blessings of existence; and had lived nearly twenty-one years in the world with very little to
distress or vex her.

She was the youngest of the two daughters of a most affectionate, indulgent father; and had, in
consequence of her sister’s marriage, been mistress of his house from a very early period. Her mother had died too long
ago for her to have more than an indistinct remembrance of her caresses; and her place had been supplied by an excellent
woman as governess, who had fallen little short of a mother in affection."""

test_tokenizers = [
    pytest.param(key, value, marks=pytest.mark.quicktest) if key == "falcon" else (key, value) for key, value in _preset_tokenizers.items()
]


@pytest.mark.parametrize("prompt_dir", [pytest.param(prompt_dirs[0], marks=pytest.mark.quicktest), *prompt_dirs])
def test_precreated_prompts(prompt_dir):
    print(prompt_dir)
    for jsonfile in prompt_dir.glob("*.jsonl"):
        with open(jsonfile) as f:
            prompt_dict = json.load(f)

        tokenizer = AutoTokenizer.from_pretrained(prompt_dict["model_id"], trust_remote_code=True)
        tokens = tokenizer(prompt_dict["prompt"])["input_ids"]
        directoryname = jsonfile.parent.stem.lower()
        assert (
            directoryname in prompt_dict["model_id"].lower()
        ), f"Directory name: {directoryname}, tokenizer model id: {prompt_dict['model_id']}"
        assert _preset_tokenizers[directoryname] == prompt_dict["model_id"]
        assert len(tokens) == prompt_dict["token_size"]


@pytest.mark.parametrize("preset_name,tokenizer_id", test_tokenizers)
def test_prompt_generator_from_preset(preset_name, tokenizer_id):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_id, trust_remote_code=True)
    for num_tokens in 16, 64, 256, 1024, 2048, 4096:
        prompt = generate_prompt(preset_name, num_tokens)
        tokens = tokenizer(prompt)["input_ids"]
        assert len(tokens) == num_tokens


@pytest.mark.parametrize("preset_name,tokenizer_id", test_tokenizers)
def test_prompt_generator_multi(preset_name, tokenizer_id):
    # token sizes that will fail on several models when \n\n is not replaced
    token_sizes = list(range(16, 256))
    with tempfile.TemporaryDirectory() as t:
        prompt_file = str(Path(t) / "prompt.jsonl")
        generate_prompt(preset_name, token_sizes, output_file=prompt_file)
        prompts = Path(prompt_file).read_text().splitlines()
        assert len(prompts) == len(token_sizes)
        for i, line in enumerate(prompts):
            prompt = json.loads(line)
            print(prompt)
            assert prompt["token_size"] == token_sizes[i]


@pytest.mark.quicktest
def test_prompt_generator_from_hub_with_source():
    model_id = "BAAI/bge-base-en-v1.5"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    for num_tokens in 4, 32, 55:
        prompt = generate_prompt(model_id, num_tokens, source_text=sample_text)
        tokens = tokenizer(prompt)["input_ids"]
        assert len(tokens) == num_tokens


@pytest.mark.quicktest
def test_cli():
    result = subprocess.run(["test-prompt-generator", "-t", "opt", "-n", "6", "-p", "Hello"], capture_output=True, text=True)
    assert "Hello Alice" in result.stderr, f"CLI output does not contain 'Hello Alice'. Output: {result.stderr}"

    result = subprocess.run(
        ["test-prompt-generator", "-t", "bigcode/starcoder2-7b", "-n", "4", "-f", __file__, "-v"],
        capture_output=True,
        text=True,
    )
    assert "import" in result.stderr, f"CLI output does not contain 'import'. Output: {result.stderr}"


@pytest.mark.quicktest
def test_cli_multi():
    with tempfile.TemporaryDirectory() as t:
        num_tokens = ["4", "8", "12"]
        prompt_file = Path(t) / "prompt.jsonl"
        # result = subprocess.run(f"test-prompt-generator -t opt -n 6 12 -o {prompt_file}", capture_output=True, text=True)
        result = subprocess.run(
            ["test-prompt-generator", "-t", "opt", "-n", *num_tokens, "-o", str(prompt_file)], capture_output=True, text=True
        )
        assert "Alice" in result.stderr, f"CLI output does not contain 'Alice'. Output: {result.stderr}"
        assert prompt_file.exists()
        prompt_file_content = prompt_file.read_text().splitlines()
        assert len(prompt_file_content) == 3
        for i, line in enumerate(prompt_file_content):
            d = json.loads(line)
            assert d["prompt"].startswith("Alice")
            assert d["token_size"] == int(num_tokens[i])


@pytest.mark.quicktest
def test_cli_overwrite():
    with tempfile.TemporaryDirectory() as t:
        prompt_file = str(Path(t) / "prompt.jsonl")
        subprocess.run(
            ["test-prompt-generator", "-t", "opt", "-n", "6", "-o", prompt_file],
            capture_output=True,
            text=True,
        )
        assert Path(prompt_file).exists()
        assert "Alice" in Path(prompt_file).read_text()
        output = subprocess.run(
            ["test-prompt-generator", "-t", "opt", "-n", "6", "-o", prompt_file],
            capture_output=True,
            text=True,
        )
        assert "FileExistsError" in output.stderr
        output = subprocess.run(
            ["test-prompt-generator", "-t", "opt", "-n", "6", "-o", prompt_file, "--overwrite"],
            capture_output=True,
            text=True,
        )
        assert "error" not in output.stderr.lower()
