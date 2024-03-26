import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from parameterized import parameterized
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


class GeneratedPromptTests(unittest.TestCase):
    @parameterized.expand(prompt_dirs)
    def test_prompt(self, prompt_dir):
        print(prompt_dir)
        for jsonfile in prompt_dir.glob("*.jsonl"):
            with open(jsonfile) as f:
                prompt_dict = json.load(f)

            tokenizer = AutoTokenizer.from_pretrained(prompt_dict["model_id"], trust_remote_code=True)
            tokens = tokenizer(prompt_dict["prompt"])["input_ids"]
            directoryname = jsonfile.parent.stem.lower()
            self.assertIn(
                directoryname,
                prompt_dict["model_id"].lower(),
                f"Directory name: {directoryname}, tokenizer model id: {prompt_dict['model_id']}",
            ),
            self.assertEqual(_preset_tokenizers[directoryname], prompt_dict["model_id"]),
            self.assertEqual(len(tokens), prompt_dict["token_size"])


class PromptGeneratorTest(unittest.TestCase):
    @parameterized.expand(_preset_tokenizers.items())
    def test_prompt_generator_from_preset(self, preset_name, tokenizer_id):
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_id, trust_remote_code=True)
        for num_tokens in 16, 32, 64, 128, 256, 1024, 2048:
            prompt = generate_prompt(preset_name, num_tokens)
            tokens = tokenizer(prompt)["input_ids"]
            self.assertEqual(len(tokens), num_tokens)

    @parameterized.expand(_preset_tokenizers)
    def test_prompt_generator_multi(self, preset_name):
        # token sizes that will fail on several models when \n\n is not replaced
        token_sizes = list(range(127, 144))
        with tempfile.TemporaryDirectory() as t:
            prompt_file = str(Path(t) / "prompt.jsonl")
            generate_prompt(preset_name, token_sizes, output_file=prompt_file)
            prompts = Path(prompt_file).read_text().splitlines()
            self.assertEqual(len(prompts), len(token_sizes))
            for i, line in enumerate(prompts):
                prompt = json.loads(line)
                print(prompt)
                self.assertEqual(prompt["token_size"], token_sizes[i])

    def test_prompt_generator_from_hub_with_source(self):
        model_id = "BAAI/bge-base-en-v1.5"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        for num_tokens in 4, 32, 55:
            prompt = generate_prompt(model_id, num_tokens, source_text=sample_text)
            tokens = tokenizer(prompt)["input_ids"]
            self.assertEqual(len(tokens), num_tokens)


class CLITest(unittest.TestCase):
    def test_cli(self):
        result = subprocess.run(
            ["test-prompt-generator", "-t", "opt", "-n", "6", "-p", "Hello"],
            capture_output=True,
            text=True,
        )
        self.assertIn(
            "Hello Alice",
            result.stderr,
            f"CLI output does not contain 'Hello Alice'. Output: {result.stderr}",
        )

        result = subprocess.run(
            [
                "test-prompt-generator",
                "-t",
                "papluca/xlm-roberta-base-language-detection",
                "-n",
                "4",
                "-f",
                __file__,
                "-v",
            ],
            capture_output=True,
            text=True,
        )
        self.assertIn(
            "import",
            result.stderr,
            f"CLI output does not contain 'import'. Output: {result.stderr}",
        )

    def test_cli_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            prompt_file = str(Path(t) / "prompt.jsonl")
            subprocess.run(
                ["test-prompt-generator", "-t", "opt", "-n", "6", "-o", prompt_file],
                capture_output=True,
                text=True,
            )
            self.assertTrue(Path(prompt_file).exists())
            self.assertIn("Alice", Path(prompt_file).read_text())
            output = subprocess.run(
                ["test-prompt-generator", "-t", "opt", "-n", "6", "-o", prompt_file],
                capture_output=True,
                text=True,
            )
            self.assertIn("FileExistsError", output.stderr)
            output = subprocess.run(
                [
                    "test-prompt-generator",
                    "-t",
                    "opt",
                    "-n",
                    "6",
                    "-o",
                    prompt_file,
                    "--overwrite",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotIn("error", output.stderr.lower())
