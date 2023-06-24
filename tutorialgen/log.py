from typing import TypedDict, Union


class MessageLog(TypedDict):
    role: str
    name: str
    content: str


class FunctionCallLog(TypedDict):
    role: str
    name: str
    arguments: dict[str, str]


def print_logs(logs: list[Union[MessageLog, FunctionCallLog]]):
    for log in logs:
        if log["role"] == "function":
            continue
            # print(f"[FUNCTION {log['name']}]")
            # print(log["content"])
            # print(f"[END FUNCTION {log['name']}]")
        if log["role"] == "function_call":
            arguments = ", ".join(
                [f"{name}={value}" for name, value in log["arguments"].items()]
            )
            print(f"executing function: {log['name']}({arguments})")
        else:
            print(f"{log['role']}: {log['content']}")
