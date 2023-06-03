import openai
import sys
import ast
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key


def parse_file(filename):
    with open(filename, "r") as source:
        tree = ast.parse(source.read())
    return tree


def extract_functions(tree):
    functions = [node for node in ast.walk(
        tree) if isinstance(node, ast.FunctionDef)]
    return functions


def generate_cheat_sheet(functions):
    cheat_sheet = {}

    for function in functions:
        code = ast.unparse(function)
        prompt = f"Explain this Python function:\n\n```python\n{code}\n```"
        response = openai.Completion.create(
            engine="text-davinci-002", prompt=prompt, temperature=0.2, max_tokens=100)

        cheat_sheet[function.name] = response.choices[0].text.strip()

    return cheat_sheet


def main():
    if len(sys.argv) != 2:
        print("Usage: generate_cheat_sheet.py <filename>")
        return

    filename = sys.argv[1]
    tree = parse_file(filename)
    functions = extract_functions(tree)
    cheat_sheet = generate_cheat_sheet(functions)

    print("Cheat Sheet:")
    for name, explanation in cheat_sheet.items():
        print(f"\nFunction: {name}")
        print(f"Explanation: {explanation}")

    # Generate markdown output
    # filename without extension + "_cheat_sheet.md"
    output_filename = filename.split('.')[0] + "_cheat_sheet.md"
    with open(output_filename, "w") as f:
        f.write("# Cheat Sheet:\n")
        for name, explanation in cheat_sheet.items():
            f.write(f"\n## Code: `{name}`\n")
            f.write(f"**Explanation:** {explanation}\n")
    print(f"Cheat sheet has been saved as '{output_filename}'.")


if __name__ == "__main__":
    main()
