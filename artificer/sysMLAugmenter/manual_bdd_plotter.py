from artificer.sysMLAugmenter.types import BDDBlock, BDDAttribute
from graphviz import Digraph
from artificer.sysMLAugmenter.util import generate_digraph

def plot_flying_machine_chapter_16_rudder_digraph():
    blocks = set()

    rudder = BDDBlock(
        block_name="rudder",
        parts={"rudder beam", "rudder wire", "rudder section","rudder frame"},
        special_children={"rear rudder", "front rudder"},
        operations={"manipulated"}
    )
    blocks.add(rudder)

    rudder_beam = BDDBlock(
        block_name="rudder beam",
        composite_parents={"rudder"},
        attributes={BDDAttribute("length", "8 ft 11 inches")}
    )

    blocks.add(rudder_beam)

    rudder_wire = BDDBlock(
        block_name="rudder wire",
        composite_parents={"rudder"},
    )

    blocks.add(rudder_wire)

    rudder_section = BDDBlock(
        block_name="rudder section",
        composite_parents={"rudder"},
        parts={"horizontal rudder section", "vertical rudder section"}
    )

    blocks.add(rudder_section)

    rudder_frame = BDDBlock(
        block_name="rudder frame",
        composite_parents={"rudder"},
    )

    blocks.add(rudder_frame)

    rear_rudder = BDDBlock(
        block_name="rear rudder",
        general_parents={"rudder"},
        composite_parents={"glider"}
    )

    blocks.add(rear_rudder)

    front_rudder = BDDBlock(
        block_name="front rudder",
        general_parents={"rudder"},
    )

    blocks.add(front_rudder)

    glider = BDDBlock(
        block_name="glider",
        parts={"rear rudder"}
    )

    blocks.add(glider)
    bdd = generate_digraph(blocks)
    bdd.render('Assets/bddDiagrams/manual_flying_machine_chapter_16_rudder_bdd', format='png', cleanup=True)

plot_flying_machine_chapter_16_rudder_digraph()