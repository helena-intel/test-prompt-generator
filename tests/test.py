from pathlib import Path

prompts_root = Path(__file__).parents[1] / "prompts"
prompt_dirs = [p for p in prompts_root.iterdir() if p.is_dir()]
