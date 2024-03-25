import os
import subprocess

from setuptools import find_packages, setup

version = "0.1"
try:
    repo_root = os.path.dirname(os.path.realpath(__file__))
    commit_id = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    version += f"+{commit_id}"
except subprocess.CalledProcessError:
    pass

setup(
    name="test-prompt-generator",
    version=version,
    url="https://github.com/helena-intel/test-prompt-generator",
    author="Helena Kloosterman",
    author_email="helena.kloosterman@intel.com",
    description="Generate LLM prompts for LLM testing with a specific input length",
    packages=find_packages(),
    package_data={"test_prompt_generator": ["text_files/alice.txt"]},
    entry_points={"console_scripts": ["test-prompt-generator=test_prompt_generator.test_prompt_generator:main"]},
)
