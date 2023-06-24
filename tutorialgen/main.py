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
            return "\n".join(result)
        else:
            with open(path, "r") as file:
                return file.read()
    except FileNotFoundError:
        return "(File not found.)"


def main():
    # set up
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    conversation = {
        "model": "gpt-3.5-turbo-16k-0613",
        "messages": [
            {
                "role": "user",
                "content": "Determine all the users inside the computer based on the directory structure, with get_file and list_dir functions.",
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
        },
    }

    start_conversation(conversation)


if __name__ == "__main__":
    main()
