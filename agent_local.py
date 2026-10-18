from ollama import chat
from main import Beam, Column, Slab, analyze, save_json

MODEL = "llama3.1:8b"
elements = []

SYSTEM_PROMPT = ("You are a civil engineering assistant. Use the tools to add beams, "
                 "columns and slabs, list and analyze them, and save the project. "
                 "Never calculate numbers yourself.")


# ================= PART 1: TOOLS (normal functions the model may ask for) =================
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


def add_column(name: str, length: float, width: float, height: float) -> str:
    """
    Add a concrete column to the project.

    Args:
        name: Column name, for example C1
        length: Section length in meters
        width: Section width in meters
        height: Column height in meters
    """
    elements.append(Column(name, float(length), float(width), float(height)))
    return f"Column {name} added. Total elements: {len(elements)}"


def add_slab(name: str, length: float, width: float, thickness: float) -> str:
    """
    Add a concrete slab to the project.

    Args:
        name: Slab name, for example S1
        length: Slab length in meters
        width: Slab width in meters
        thickness: Slab thickness in meters
    """
    elements.append(Slab(name, float(length), float(width), float(thickness)))
    return f"Slab {name} added. Total elements: {len(elements)}"


def list_elements() -> str:
    """
    List all elements added so far, with volume and weight.
    """
    if len(elements) == 0:
        return "No elements added yet."
    return "\n".join(e.describe() for e in elements)


def analyze_project() -> str:
    """
    Calculate total volume, total weight, maximum bending moment and
    maximum shear force of all elements added so far.
    """
    return "\n".join(analyze(elements))


def save_project() -> str:
    """
    Save all elements to the file elements.json.
    """
    save_json(elements)
    return f"Saved {len(elements)} element(s) to elements.json"


# ================= PART 2: THE TOOL LIST (name -> function) =================
TOOLS = {
    "add_beam": add_beam,
    "add_column": add_column,
    "add_slab": add_slab,
    "list_elements": list_elements,
    "analyze_project": analyze_project,
    "save_project": save_project,
}


# ================= PART 3: THE AGENT LOOP =================
def run_agent(messages, max_steps=6):
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


# ================= PART 4: THE CHAT (this part runs when you start the file) =================
if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Type your request. Type quit to stop.")
    while True:
        request = input("\nYou: ").strip()
        if request.lower() == "quit":
            break
        if request == "":
            continue
        messages.append({"role": "user", "content": request})
        print("Agent:", run_agent(messages))