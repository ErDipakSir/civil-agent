from ollama import chat
from main import Beam, analyze

MODEL = "llama3.1:8b"
elements = []


# ---------- Tools: normal functions the model may ask for ----------
def add_beam(name: str, length: float, width: float, depth: float, load: float) -> str:
    """
    Add a concrete beam to the project.

    Args:
        name: Beam name, for example B1
        length: Span length in meters
        width: Beam width in meters
        depth: Beam depth in meters
        load: Uniform load in kN per meter
    """
    elements.append(Beam(name, float(length), float(width), float(depth), float(load)))
    return f"Beam {name} added. Total elements: {len(elements)}"


def analyze_project() -> str:
    """
    Calculate total volume, total weight, maximum bending moment and
    maximum shear force of all elements added so far.
    """
    return "\n".join(analyze(elements))


TOOLS = {"add_beam": add_beam, "analyze_project": analyze_project}


# ---------- The agent loop ----------
def run_agent(user_text, max_steps=6):
    messages = [
        {"role": "system",
         "content": "You are a civil engineering assistant. Use the tools to add "
                    "beams and analyze them. Never calculate numbers yourself."},
        {"role": "user", "content": user_text},
    ]

    for step in range(max_steps):
        response = chat(MODEL, messages=messages, tools=list(TOOLS.values()))
        messages.append(response.message)

        if not response.message.tool_calls:
            return response.message.content          # no tool needed: final answer

        for call in response.message.tool_calls:
            name = call.function.name
            args = call.function.arguments
            print(f"Step {step + 1}: model wants {name}({args})")

            func = TOOLS.get(name)
            if func is None:
                result = f"Error: unknown tool {name}"
            else:
                try:
                    result = func(**args)
                except (TypeError, ValueError) as error:
                    result = f"Error: {error}"

            print(f"   tool result: {result}")
            messages.append({"role": "tool", "content": str(result), "tool_name": name})

    return "Stopped: too many steps."


if __name__ == "__main__":
    request = input("What should the agent do? ")
    print("\nFinal answer:")
    print(run_agent(request))