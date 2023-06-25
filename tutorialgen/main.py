import os
from dotenv import load_dotenv
import openai

from conversation import start_conversation


def get_file(path: str):
    try:
        if os.path.isdir(path):
            result = []
            dirs = os.listdir(path)
            for dir in dirs:
                if os.path.isdir(dir):
                    result.append(f"Directory: {dir}")
                else:
                    result.append(f"File: {dir}")
            return f"(Opening directory: {path})\n".join(result)
        else:
            with open(path, "r", encoding="utf-8") as file:
                return f"(Opening file: {path})\n" + file.read()
    except FileNotFoundError:
        return "(File or directory not found.)"


def write_file(isdir: bool, path: str, content: str = "", append: bool = False) -> str:
    if isdir:
        os.makedirs(path, exist_ok=True)
    else:
        dirname = os.path.dirname(path)
        if len(dirname) > 0:
            os.makedirs(dirname, exist_ok=True)

        if append:
            with open(path, "a", encoding="utf-8") as file:
                file.write(content)
        else:
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
    return "(Done.)"


def main():
    # set up
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    conversation = {
        "model": "gpt-3.5-turbo-16k-0613",
        "messages": [
            {
                "role": "user",
                "content": """
                I'd like to create a step-by-step tutorial for my library, next-pipe.
                The contents of the library exists in \"C:/Users/main/Desktop/projects/next-pipe\".
                Please understand how the library works by reading README.md or any other source files with \"get_file\".
                After that, please create a step-by-step tutorial in the file \"tutorial.md\" using \"write_file\" command, inside the library repository.
                """,
            },
        ],
        "functions": {
            "get_file": {
                "description": "Get the contents of a file, or a list of files in a directory.",
                "properties": [
                    {
                        "name": "path",
                        "type": "string",
                        "description": "The path to the file or directory.",
                        "required": True,
                    }
                ],
                "function": get_file,
            },
            "write_file": {
                "description": "Write content to a file, or create a directory.",
                "properties": [
                    {
                        "name": "isdir",
                        "type": "boolean",
                        "description": "Whether the path is a directory.",
                        "required": True,
                    },
                    {
                        "name": "path",
                        "type": "string",
                        "description": "The path to the file or directory.",
                        "required": True,
                    },
                    {
                        "name": "content",
                        "type": "string",
                        "description": "The content to write to the file.",
                        "required": False,
                    },
                    {
                        "name": "append",
                        "type": "boolean",
                        "description": "Whether to append the content to the file.",
                        "required": False,
                    },
                ],
                "function": write_file,
            },
        },
    }

    start_conversation(conversation)


if __name__ == "__main__":
    main()
