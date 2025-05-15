from dynamo.sysMLAugmenter.types import BDDBlock

from graphviz import Digraph

def generate_digraph(blocks: set[BDDBlock], without_connections = False) -> Digraph:
    bdd = Digraph('bdd', node_attr={'shape': 'record', 'fontsize': '10'}, format='png')
    block_names = [block.block_name for block in blocks]

    def addBlockAsNode(block: BDDBlock):
        if block.isAugmented:
            bdd.node(block.block_name, block.to_label(), style='dotted')
        else:
            bdd.node(block.block_name, block.to_label())

    for block in blocks:
        addBlockAsNode(block)
    
    if not without_connections:
        for block in blocks:
            for general_parent in block.general_parents:
                if general_parent in block_names:
                    bdd.edge(block.block_name, general_parent, label="Generalization", arrowhead="onormal")
            for composite_parent in block.composite_parents:
                if composite_parent in block_names:
                    bdd.edge( block.block_name, composite_parent, label="Composite", arrowhead="odiamond")
            for reference_parent in block.reference_parents:
                if reference_parent in block_names:
                    bdd.edge( block.block_name, reference_parent, label="Reference", arrowhead="vee")
    
    return bdd