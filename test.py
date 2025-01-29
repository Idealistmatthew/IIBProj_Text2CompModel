from dynamo.sysMLAugmenter.types import BDDAttribute, BDDBlock
import json

attribute = BDDAttribute("name", "type", "description", "test")



print(attribute.toJSON())

print(BDDAttribute.fromJSON(attribute.toJSON()))

bddBlock = BDDBlock("block_name",
                    True,
                    ["operations"],
                    ["general_parents"], ["special_children"], ["composite_parents"], ["reference_parents"], ["reference_children"], [attribute], ["parts"])

print(bddBlock.toJSON())

print(BDDBlock.fromJSON(bddBlock.toJSON()))