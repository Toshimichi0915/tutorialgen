import json
from typing import Callable, TypedDict, Union
from log import MessageLog, FunctionCallLog, print_logs

import openai


class Message(TypedDict):
    role: str
    name: str
    content: str


class FunctionProperty(TypedDict):
    name: str
    type: str
    description: str
    required: bool


class FunctionCall(TypedDict):
    name: str
    description: str
    properties: list[FunctionProperty]
    function: Callable


class Conversation(TypedDict):
    model: str
    messages: list[Message]
    functions: dict[str, FunctionCall]
    logs: list[Union[MessageLog, FunctionCallLog]]


def conv_functions(functions: dict[str, FunctionCall]) -> list:
    result = []
    for name, function in functions.items():
        properties = {}
        required = []
        for property in function["properties"]:
            properties[property["name"]] = {
                "type": property["type"],
                "description": property["description"],
            }

            if property["required"]:
                required.append(property["name"])

        result.append(
            {
                "name": name,
                "description": function["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
        )

    return result


def start_conversation(conversation: Conversation) -> Conversation:
    conversation["logs"] = []
    conversation["logs"].extend(conversation["messages"])
    while True:
        # call OpenAI API
        response = openai.ChatCompletion.create(
            model=conversation["model"],
            messages=conversation["messages"],
            functions=conv_functions(conversation["functions"]),
        )

        if len(response["choices"]) != 1:
            raise Exception("Expected one response from OpenAI API.")

        message = response["choices"][0]["message"]

        # handle response
        should_continue = False

        if "function_call" in message:
            # find function
            func_name = message["function_call"]["name"]
            arguments = json.loads(message["function_call"]["arguments"])

            if not func_name in conversation["functions"]:
                arguments = ", ".join(
                    [f"{name}={value}" for name, value in arguments.items()]
                )
                raise Exception(
                    f"Function {message['function_call']['name']}({arguments}) not found."
                )

            target = conversation["functions"][func_name]
            if not target:
                raise Exception(
                    f"Function {message['function_call']['name']} not found."
                )

            # log function call
            conversation["logs"].append(
                {
                    "role": "function_call",
                    "name": func_name,
                    "arguments": arguments,
                }
            )

            # add function call to conversation, and continue
            result = target["function"](**arguments)
            conversation["messages"].append(
                {
                    "role": "function",
                    "name": func_name,
                    "content": result,
                }
            )
            conversation["logs"].append(
                {
                    "role": "function",
                    "name": message["function_call"]["name"],
                    "content": result,
                }
            )

            should_continue = True
        else:
            # add message to conversation
            conversation["messages"].append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )
            conversation["logs"].append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

        print_logs(conversation["logs"])
        print("-----")
        if should_continue:
            continue

        return conversation
