from pathlib import Path
from jinja2 import FileSystemLoader, Environment
import spacy


templates_path = Path(__file__).resolve().parent / 'function_templates'
loader = FileSystemLoader(templates_path)
env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

function_edit_templates_path = Path(__file__).resolve().parent / 'function_edit_templates'
function_edit_loader = FileSystemLoader(function_edit_templates_path)
function_edit_env = Environment(loader=function_edit_loader, trim_blocks=True, lstrip_blocks=True)

nlp = spacy.load("en_core_web_sm")


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
        self.function_states = function_states
        self.function_body = self.generate_function_body()
    
    def generate_function_body(self):
        pass

constant_dict = {
    "gravity": 9.81,
    "gravitational_constant": 6.67430e-11,
}

dynamical_function_dict = { 
    "SimplePendulumOscillation":
    DynamicalSystemFunction(
        function_name="SimplePendulumOscillation",
        function_descriptors=[
            "A simple pendulum consists of a mass (bob) attached to a fixed point by an inextensible string. Gravity drives the swinging motion. For small angular displacements, the motion is periodic and can be modeled as simple harmonic motion. The period of oscillation depends on the length of the string and the acceleration due to gravity."
        ],
        function_body_template="simple_pendulum_oscillation.jinja2",
        function_states=["angle", "angular_velocity"],
        function_args=["length", "gravity"]
    ),
    "MassSpringOscillation" :
    DynamicalSystemFunction(
        function_name="MassSpringOscillation",
        function_descriptors=[
            "A mass-spring system consists of a mass attached to a spring. The spring exerts a restoring force proportional to the displacement from its equilibrium position. The motion is periodic and can be modeled as simple harmonic motion. The period of oscillation depends on the mass and the spring constant."
        ],
        function_body_template="mass_spring_oscillation.jinja2",
        function_states=["displacement", "velocity"],
        function_args=["mass", "spring_constant", "previous_displacement", "previous_velocity", "time_step"]
    )

}

function_descriptors_to_function_dict = {}

for function in dynamical_function_dict.values():
    for descriptor in function.function_descriptors:
        function_descriptors_to_function_dict[descriptor] = function.function_name

# def generate_function_parameters(function_args_to_retain: list[str]):
#     function_parameters = function_args_to_retain.copy()
#     # for function in dynamical_function_dict.values():
#     #     for arg in function.function_args:
#     #         if arg not in function_parameters:
#     #             function_parameters.append(arg)
#     stringified_function_parameters = ", ".join(function_parameters)
#     return stringified_function_parameters

def match_args(arg, class_attributes, surrounding_numeric_attributes):
    for category, attributes in class_attributes.items():
        if category.lower() == arg.lower():
            return f"self.{attributes}"
    for system_component, category in surrounding_numeric_attributes.items():
        if category.lower() == arg.lower():
            return f"{system_component}.{category}"
    return 1 # default value

class GuessFunctionResult:
    def __init__(self, function_implementation: str, init_append: str, 
                 new_init_interface: str):
        self.function_implementation = function_implementation
        self.new_init_interface = new_init_interface
        self.init_append = init_append

    def __repr__(self):
        return f"GuessFunctionResult(function_implementation={self.function_implementation}, new_init_interface={self.new_init_interface}, init_append={self.init_append})"

def guess_function(function_name: str,  
                   function_args_to_retain: list[str],
                   ClassName: str,
                   function_prompt: str,
                   class_attributes: list[dict[str, str]],
                   surrounding_numeric_attributes: list[dict[str, str]],):
    function_descs_to_check = function_descriptors_to_function_dict.keys()
    tokenized_function_prompt = nlp(function_prompt)
    current_max_similarity = 0
    current_guessed_function_name = None
    for function_descriptor in function_descs_to_check:
        similarity_score = tokenized_function_prompt.similarity(nlp(function_descriptor))
        if similarity_score > current_max_similarity:
            current_max_similarity = similarity_score
            current_guessed_function_name = function_descriptors_to_function_dict[function_descriptor]
    if current_guessed_function_name is not None and current_max_similarity > 0.5:
        print(f"Guessed function name: {current_guessed_function_name}")
        print(f"Similarity score: {current_max_similarity}")
        dynamical_system_function = dynamical_function_dict[current_guessed_function_name]
        function_template = env.get_template(dynamical_system_function.function_body_template)

        render_dict = {
            "function_name": function_name,
            "function_prompt": function_prompt,
        }

        for arg in dynamical_system_function.function_args:
            if arg in constant_dict:
                render_dict[arg] = constant_dict[arg]
            else:
                render_dict[arg] = match_args(arg, class_attributes, surrounding_numeric_attributes)
        function_implementation = function_template.render(render_dict)

        init_append = function_edit_env.get_template("init_append_template.jinja2").render({
            "function_states": dynamical_system_function.function_states,
        })
        initial_states = [ f"initial_{state}" for state in dynamical_system_function.function_states]
        new_init_interface = f"def __init__(self, {', '.join(initial_states)}):\n"
        return GuessFunctionResult(function_implementation=function_implementation,
                                   init_append=init_append,
                                   new_init_interface=new_init_interface)
                                   
    


guess_function_result = guess_function(
    function_name="CanBeApproximated",
    function_args_to_retain=["self"],
    ClassName="Motion",
    function_prompt="Gravity causes the pendulum to swing .The motion is periodic and can be approximated by simple harmonic motion for small angles .The pendulum 's period depends on period length and gravity .",
    class_attributes={"Type": "periodic", "Approximation": "simple harmonic", "Condition": "small angles", "Angle": "small"},
    surrounding_numeric_attributes={"Bob": "weight" , "String": "Length"},
)

print(guess_function_result.function_implementation)

print(guess_function_result.new_init_interface)

print(guess_function_result.init_append)