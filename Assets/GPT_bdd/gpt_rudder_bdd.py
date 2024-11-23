from graphviz import Digraph

# Create a new Digraph for the BDD
bdd_diagram = Digraph("BDD_Rudder", format="png")
bdd_diagram.attr(rankdir="TB", size="8,10")

# Define the main component
bdd_diagram.node("Rudder", shape="box", style="filled", color="lightblue", fontsize="12")

# Add subcomponents as blocks
subcomponents = [
    ("Vertical Rudder", "lightgreen"),
    ("Horizontal Rudder", "lightgreen"),
    ("Rudder Beam", "lightyellow"),
    ("Cross Pieces", "lightyellow"),
    ("Guy Wires", "lightcoral"),
    ("Turn-Buckles", "lightcoral"),
]

for name, color in subcomponents:
    bdd_diagram.node(name, shape="box", style="filled", color=color, fontsize="10")

# Define relationships
bdd_diagram.edges([
    ("Rudder", "Vertical Rudder"),
    ("Rudder", "Horizontal Rudder"),
    ("Rudder", "Rudder Beam"),
    ("Rudder Beam", "Cross Pieces"),
    ("Rudder", "Guy Wires"),
    ("Guy Wires", "Turn-Buckles"),
    ("Vertical Rudder", "Horizontal Rudder"),
])

# Render the diagram to a file
output_path = "BDD_Rudder.png"
bdd_diagram.render(output_path, cleanup=True)
