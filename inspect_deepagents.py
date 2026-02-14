import deepagents
import inspect
import sys

with open("deepagents_info.txt", "w") as f:
    f.write(f"deepagents dir: {dir(deepagents)}\n")
    try:
        f.write(f"create_deep_agent signature: {inspect.signature(deepagents.create_deep_agent)}\n")
    except Exception as e:
        f.write(f"Error inspecting create_deep_agent: {e}\n")
    
    try:
        f.write(f"backends dir: {dir(deepagents.backends)}\n")
    except Exception as e:
        f.write(f"Error inspecting backends: {e}\n")

print("Done writing info")
