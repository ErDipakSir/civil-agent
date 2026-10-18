# Civil Agent

A Python project for simple reinforced concrete calculations, with two ways to use it:
a menu-driven toolkit, and an AI agent that runs on a local language model and calls the
same calculation code from plain English.

## What it does

- **Toolkit (`main.py`):** add beams, columns, and slabs; see volume and weight; analyze
  bending moment and shear force of beams; save and load the project as JSON.
- **Agent (`agent_local.py`):** type a request in plain English, and a local model
  (Ollama, `llama3.1:8b`) decides which tool to run. The model never does the math. The
  tools call the same classes as the toolkit.
- **Tests (`test_main.py`):** automatic checks that the formulas still give the right numbers.

## Features

- Object-oriented design with inheritance (`Element`, `Beam`, `Column`, `Slab`)
- Input validation for numbers and names
- NumPy analysis: totals, maximum, average, and the critical beam
- JSON saving and loading
- Agent with six tools: add beam, add column, add slab, list elements, analyze, save
- Runs fully on your own computer, with no API key and no cost

## Requirements

- Python 3
- The libraries in `requirements.txt` (`numpy`, `ollama`, `pytest`)
- [Ollama](https://ollama.com) with the model `llama3.1:8b` (about 5 GB download)

## Setup

```
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull llama3.1:8b
```

## How to run

**Toolkit (menu):**

```
python main.py
```

**Agent (chat in plain English).** Make sure Ollama is running, then:

```
python agent_local.py
```

Type each request at the `You:` line. Type `quit` to stop.

**Tests:**

```
pytest
```

## Example

Agent session:

```
You: Add beam B1 (6 m, 0.3 m wide, 0.5 m deep, 10 kN/m), column C1 (0.3 m by 0.3 m, 3 m high), and slab S1 (6 m by 4 m, 0.15 m thick).
You: List the elements and analyze the project.
```

Expected analysis:

```
Number of elements: 3
Total volume: 4.770 m3
Total weight: 119.25 kN
Heaviest element: S1 (90.00 kN)
Maximum bending moment: 45.00 kNm (beam B1)
Average bending moment: 45.00 kNm
Maximum shear force: 30.00 kN (beam B1)
```

## Formulas used

For a simply supported beam of span L (m) with a uniform load w (kN/m):

| Quantity | Formula |
| --- | --- |
| Maximum bending moment | w x L^2 / 8 |
| Maximum shear force | w x L / 2 |
| Weight of an element | volume x 25 kN/m3 (reinforced concrete) |

## Assumptions and limits

- Beams are simply supported with a uniform load over the full span.
- The unit weight of concrete is fixed at 25 kN/m3.
- A small local model can make mistakes, such as choosing the wrong tool. All numbers come
  from the tested calculation code, and the agent has a step limit.
- This is a learning project and does not replace a full structural design check.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Classes, JSON saving and loading, NumPy analysis, and the menu |
| `agent_local.py` | Tools and the agent loop that talks to the local model |
| `test_main.py` | Automatic tests for the formulas and the analysis |
| `requirements.txt` | Libraries the project needs |

## Author

Dipak Pangyani, civil engineer learning AI engineering