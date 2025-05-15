from pathlib import Path
from jinja2 import FileSystemLoader, Environment


templates_path = Path(__file__).resolve().parent / 'function_templates'
loader = FileSystemLoader(templates_path)
env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
class_template = 'class.jinja2'
# self.class_template = env.get_template(class_template)



class DynamicalSystemFunction:
    def __init__(self,
                 function_name: str,
                 function_descriptors: list[str],
                 function_body_template: str,
                 function_states: list[str],
                    function_args: list[str]):
        self.function_name = function_name
        self.function_descriptors = function_descriptors
        self.function_body_template = function_body_template
        self.function_args = function_args
        self.function_states = []
        self.function_body = self.generate_function_body()
    
    def generate_function_body(self):
        pass




[
    DynamicalSystemFunction(
        function_name="SimplePendulumOscillation",
        function_descriptors=[
            "A simple pendulum consists of a mass (bob) attached to a fixed point by an inextensible string. Gravity drives the swinging motion. For small angular displacements, the motion is periodic and can be modeled as simple harmonic motion. The period of oscillation depends on the length of the string and the acceleration due to gravity."
        ],
        function_body_template="",
        function_states=["angle"]
        function_args=["mass", "length"]

    )
]





def guess_function(function_name: str,  
                   function_args_to_retain: list[str],
                   ClassName: str,
                   function_prompt: str,
                   class_attributes: list[dict[str, str]],
                   surrounding_numeric_attributes: list[dict[str, str]],):
    


    pass





guess_function(
    function_name="CanBeApproximated",
    function_args_to_retain=["self"],
    ClassName="Motion",
    function_prompt="Gravity causes the pendulum to swing .The motion is periodic and can be approximated by simple harmonic motion for small angles .The pendulum 's period depends on period length and gravity .",
    class_attributes=[{"Type": "periodic"}, {"Approximation": "simple harmonic"}, {"Condition": "small angles"}, {"Angle": "small"}],
    surrounding_numeric_attributes=[{"Bob": "Weight"}, {"String": "Length"}],
)