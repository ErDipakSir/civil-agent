import json
import numpy as np

DATA_FILE = "elements.json"


# ---------- Input helpers ----------
def get_int_number(message):
    while True:
        try:
            number = int(input(message))
        except ValueError:
            print("Invalid input. Please enter a whole number.")
            continue
        if number <= 0:
            print("Please enter a number greater than zero.")
        else:
            return number


def get_number(message):
    while True:
        try:
            number = float(input(message))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if number <= 0:
            print("Please enter a number greater than zero.")
        else:
            return number


def get_name(message):
    while True:
        text = input(message).strip()
        if text == "":
            print("Name cannot be empty.")
        else:
            return text


# ---------- Classes (inheritance) ----------
class Element:
    kind = "Element"

    def __init__(self, name, density=25):
        self.name = name
        self.density = density              # kN/m3 for RCC

    def volume(self):
        return 0                            # each child replaces this

    def weight(self):
        return self.volume() * self.density

    def describe(self):
        return (f"{self.kind} {self.name}: volume = {self.volume():.3f} m3, "
                f"weight = {self.weight():.2f} kN")

    def to_dict(self):
        return {"kind": self.kind, "name": self.name}


class Beam(Element):
    kind = "Beam"

    def __init__(self, name, length, width, depth, load):
        super().__init__(name)
        self.length = length
        self.width = width
        self.depth = depth
        self.load = load                    # kN per meter

    def volume(self):
        return self.length * self.width * self.depth

    def total_load(self):
        return self.load * self.length

    def bending_moment(self):
        return self.load * self.length ** 2 / 8     # simply supported, uniform load

    def shear_force(self):
        return self.load * self.length / 2

    def describe(self):
        return (super().describe() +
                f", M = {self.bending_moment():.2f} kNm, V = {self.shear_force():.2f} kN")

    def to_dict(self):
        data = super().to_dict()
        data.update({"length": self.length, "width": self.width,
                     "depth": self.depth, "load": self.load})
        return data


class Column(Element):
    kind = "Column"

    def __init__(self, name, length, width, height):
        super().__init__(name)
        self.length = length
        self.width = width
        self.height = height

    def volume(self):
        return self.length * self.width * self.height

    def to_dict(self):
        data = super().to_dict()
        data.update({"length": self.length, "width": self.width, "height": self.height})
        return data


class Slab(Element):
    kind = "Slab"

    def __init__(self, name, length, width, thickness):
        super().__init__(name)
        self.length = length
        self.width = width
        self.thickness = thickness

    def volume(self):
        return self.length * self.width * self.thickness

    def to_dict(self):
        data = super().to_dict()
        data.update({"length": self.length, "width": self.width, "thickness": self.thickness})
        return data


# ---------- JSON saving and loading ----------
def element_from_dict(d):
    kind = d["kind"]
    if kind == "Beam":
        return Beam(d["name"], d["length"], d["width"], d["depth"], d["load"])
    elif kind == "Column":
        return Column(d["name"], d["length"], d["width"], d["height"])
    elif kind == "Slab":
        return Slab(d["name"], d["length"], d["width"], d["thickness"])
    raise ValueError(f"unknown kind: {kind}")


def save_json(elements):
    data = [e.to_dict() for e in elements]
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_json():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []                           # first run: no file yet
    except json.JSONDecodeError:
        print("Data file is damaged. Starting with an empty list.")
        return []

    elements = []
    for item in data:
        try:
            elements.append(element_from_dict(item))
        except (KeyError, ValueError) as error:
            print(f"Skipped a bad record: {error}")
    return elements


# ---------- Analysis with NumPy ----------
def analyze(elements):
    if len(elements) == 0:
        return ["No elements added yet."]

    volumes = np.array([e.volume() for e in elements])
    weights = np.array([e.weight() for e in elements])
    lines = [
        f"Number of elements: {len(elements)}",
        f"Total volume: {volumes.sum():.3f} m3",
        f"Total weight: {weights.sum():.2f} kN",
        f"Heaviest element: {elements[np.argmax(weights)].name} ({weights.max():.2f} kN)",
    ]

    beams = [e for e in elements if isinstance(e, Beam)]
    if beams:
        moments = np.array([b.bending_moment() for b in beams])
        shears = np.array([b.shear_force() for b in beams])
        lines.append(f"Maximum bending moment: {moments.max():.2f} kNm "
                     f"(beam {beams[np.argmax(moments)].name})")
        lines.append(f"Average bending moment: {moments.mean():.2f} kNm")
        lines.append(f"Maximum shear force: {shears.max():.2f} kN "
                     f"(beam {beams[np.argmax(shears)].name})")
    else:
        lines.append("No beams added, so there are no moment or shear results.")
    return lines


# ---------- Menu actions ----------
def add_beam(elements):
    print("Enter the beam details:")
    name = get_name("Beam name: ")
    length = get_number("Length (m): ")
    width = get_number("Width (m): ")
    depth = get_number("Depth (m): ")
    load = get_number("Load (kN/m): ")
    elements.append(Beam(name, length, width, depth, load))
    print(f"Beam {name} added.")


def add_column(elements):
    print("Enter the column details:")
    name = get_name("Column name: ")
    length = get_number("Length (m): ")
    width = get_number("Width (m): ")
    height = get_number("Height (m): ")
    elements.append(Column(name, length, width, height))
    print(f"Column {name} added.")


def add_slab(elements):
    print("Enter the slab details:")
    name = get_name("Slab name: ")
    length = get_number("Length (m): ")
    width = get_number("Width (m): ")
    thickness = get_number("Thickness (m): ")
    elements.append(Slab(name, length, width, thickness))
    print(f"Slab {name} added.")


def show_all(elements):
    if len(elements) == 0:
        print("No elements added yet.")
        return
    print("\nAll elements:")
    for e in elements:
        print(e.describe())


def menu():
    while True:
        print("\nCivil Structure Toolkit")
        print("1. Add beam")
        print("2. Add column")
        print("3. Add slab")
        print("4. Show all elements")
        print("5. Analysis (NumPy)")
        print("6. Save and exit")
        choice = get_int_number("Choose option 1 to 6: ")
        if 1 <= choice <= 6:
            return choice
        print("Choose between 1 and 6.")


# ---------- Main program ----------
if __name__ == "__main__":
    elements = load_json()
    print(f"{len(elements)} element(s) loaded from {DATA_FILE}.")

    while True:
        choice = menu()
        if choice == 1:
            add_beam(elements)
        elif choice == 2:
            add_column(elements)
        elif choice == 3:
            add_slab(elements)
        elif choice == 4:
            show_all(elements)
        elif choice == 5:
            print()
            for line in analyze(elements):
                print(line)
        elif choice == 6:
            save_json(elements)
            print(f"Saved to {DATA_FILE}. Goodbye!")
            break