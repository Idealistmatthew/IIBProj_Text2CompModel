from graphviz import Digraph

# Refine the diagram to match a proper BDD structure using Graphviz

bdd_diagram = Digraph("Proper_BDD_Rudder", format="png")

bdd_diagram.attr(rankdir="TB", size="8,10")



# Define the main block (Rudder)

bdd_diagram.node("Rudder", label="{Rudder|Attributes: Length, Cloth-Covered|Responsibilities: Stability, Wind Orientation}", 

                 shape="record", style="filled", color="lightblue", fontsize="10")



# Subcomponents as blocks with attributes/responsibilities

bdd_diagram.node("VerticalRudder", 

                 label="{Vertical Rudder|Attributes: Uprights (3'10\"), Spacing (2')|Responsibilities: Keeps head to wind}", 

                 shape="record", style="filled", color="lightgreen", fontsize="10")



bdd_diagram.node("HorizontalRudder", 

                 label="{Horizontal Rudder|Attributes: Frame (6' x 2')|Responsibilities: Preserves equilibrium}", 

                 shape="record", style="filled", color="lightgreen", fontsize="10")



bdd_diagram.node("RudderBeam", 

                 label="{Rudder Beam|Attributes: Length (8'11\")|Responsibilities: Frame support for rudders}", 

                 shape="record", style="filled", color="lightyellow", fontsize="10")



bdd_diagram.node("CrossPieces", 

                 label="{Cross Pieces|Attributes: Length (2'), Material (Light)|Responsibilities: Connect beams to struts}", 

                 shape="record", style="filled", color="lightyellow", fontsize="10")



bdd_diagram.node("GuyWires", 

                 label="{Guy Wires|Attributes: Material (No. 12 piano wire)|Responsibilities: Structural reinforcement}", 

                 shape="record", style="filled", color="lightcoral", fontsize="10")



bdd_diagram.node("TurnBuckles", 

                 label="{Turn-Buckles|Attributes: Adjustable tension|Responsibilities: Regulate wire tension}", 

                 shape="record", style="filled", color="lightcoral", fontsize="10")



# Define relationships (composition/association)

bdd_diagram.edge("Rudder", "VerticalRudder", label="Composed of")

bdd_diagram.edge("Rudder", "HorizontalRudder", label="Composed of")

bdd_diagram.edge("Rudder", "RudderBeam", label="Composed of")

bdd_diagram.edge("RudderBeam", "CrossPieces", label="Connected via")

bdd_diagram.edge("Rudder", "GuyWires", label="Reinforced by")

bdd_diagram.edge("GuyWires", "TurnBuckles", label="Regulated by")

bdd_diagram.edge("VerticalRudder", "HorizontalRudder", label="Connected")



# Render the diagram

output_path_proper = "Proper_BDD_Rudder.png"

bdd_diagram.render(output_path_proper, cleanup=True)
