import openai
import os
import sys
from rich import print
import click
from typing import Optional
import csv
from urllib.request import urlopen
import codecs
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyWordCompleter


openai.api_key = os.environ["OPENAI_API_KEY"]

EXIT_COMMANDS = [":exit", ":quit"]
INPUT_PROMPT = "[bold cyan]PROMPT>[/bold cyan] "
OPENAI_MODEL = "gpt-3.5-turbo"


@click.command()
@click.option(
    "--initial-prompt-title",
    help="""The initial prompt sent to the model.
    This supports the prompts written in https://github.com/f/awesome-chatgpt-prompts for more details.
    ex) Linux Terminal""",
)
@click.option(
    "--select-initial-prompt",
    "-p",
    is_flag=True,
    default=False,
)
def cli(
    initial_prompt_title: Optional[str],
    select_initial_prompt: bool,
):
    print(
        "Type {} to exit".format(
            " or ".join(map(lambda s: '"' + s + '"', EXIT_COMMANDS))
        )
    )

    messages = []

    def chat(prompt: str):
        messages.append({"role": "user", "content": prompt})
        completion = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
        )
        res = completion["choices"][0]["message"]["content"].strip()
        print(res, flush=True)
        messages.append({"role": "system", "content": res})

    if initial_prompt_title and select_initial_prompt:
        print(
            "You can specify one of --initial-prompt-title and --select-initial-prompt, not both"
        )
        return

    if initial_prompt_title:
        initial_prompt_dict = read_initial_prompt_dict()
        initial_prompt = initial_prompt_dict[initial_prompt_title]
        print(INPUT_PROMPT, end="", flush=True)
        print(initial_prompt, flush=True)
        chat(initial_prompt)

    if select_initial_prompt:
        initial_prompt_dict = read_initial_prompt_dict()
        session: PromptSession = PromptSession(
            complete_while_typing=True,
            complete_in_thread=True,
            bottom_toolbar="[Tab] autocompletion",
        )
        initial_prompt_title = session.prompt(
            message="INITIAL_PROMPT> ",
            completer=FuzzyWordCompleter(list(initial_prompt_dict.keys())),
            placeholder="ex) Linux Terminal",
        )
        if initial_prompt_title:
            initial_prompt = initial_prompt_dict[initial_prompt_title]
            print(INPUT_PROMPT, end="", flush=True)
            print(initial_prompt, flush=True)
            chat(initial_prompt)

    print(INPUT_PROMPT, end="", flush=True)
    for prompt in sys.stdin:
        prompt = prompt.strip()
        if prompt in EXIT_COMMANDS:
            break
        chat(prompt)
        print(INPUT_PROMPT, end="", flush=True)


def read_initial_prompt_dict() -> dict[str, str]:
    res = urlopen(
        "https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/main/prompts.csv"
    )
    csvfile = csv.reader(codecs.iterdecode(res, "utf-8"))
    result = {}
    for line in csvfile:
        result[line[0]] = line[1]
    return result


def main():
    cli()


if __name__ == "__main__":
    main()
