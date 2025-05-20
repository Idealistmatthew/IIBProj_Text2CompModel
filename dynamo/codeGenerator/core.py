from pathlib import Path
from jinja2 import FileSystemLoader, Environment
import spacy





class DynamicalSystemFunction:
    def __init__(self,
                 function_name: str,
                 function_descriptors: list[str],
                 function_body_template: str,
                 function_states: list[str],
                function_args: list[str],
                required_imports: list[str]):
        self.function_name = function_name
        self.function_descriptors = function_descriptors
        self.function_body_template = function_body_template
        self.function_args = function_args
        self.function_states = function_states
        self.required_imports = required_imports
        self.function_body = self.generate_function_body()
    
    def generate_function_body(self):
        pass

class GuessFunctionResult:
    def __init__(self, function_implementation: str, function_states: list[str], 
                 new_init_interface: str,
                 simulate_function: str,
                 required_imports: list[str] = None,
                 matched_system_components: list[str] = None):
        self.function_implementation = function_implementation
        self.function_states = function_states
        self.new_init_interface = new_init_interface
        self.simulate_function = simulate_function
        self.required_imports = required_imports
        self.matched_system_components = matched_system_components

    def __repr__(self):
        return f"GuessFunctionResult(function_implementation={self.function_implementation}, new_init_interface={self.new_init_interface}, init_append={self.init_append})"

class CodeGenerator:
    def __init__(self):
        templates_path = Path(__file__).resolve().parent / 'function_templates'
        loader = FileSystemLoader(templates_path)
        self.env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

        function_edit_templates_path = Path(__file__).resolve().parent / 'function_edit_templates'
        function_edit_loader = FileSystemLoader(function_edit_templates_path)
        self.function_edit_env = Environment(loader=function_edit_loader, trim_blocks=True, lstrip_blocks=True)
        self.nlp = spacy.load("en_core_web_sm")

        self.constant_dict = {
            "gravity": 9.81,
            "gravitational_constant": 6.67430e-11,
        }

        self.dynamical_function_dict = { 
            "SimplePendulumOscillation":
            DynamicalSystemFunction(
                function_name="SimplePendulumOscillation",
                function_descriptors=[
                    "A simple pendulum consists of a mass (bob) attached to a fixed point by an inextensible string. Gravity drives the pendulum to swing. For small angular displacements, the motion is periodic and can be modeled as simple harmonic motion. The pendulum's period depends on the string's length and gravity."
                ],
                function_body_template="simple_pendulum_oscillation.jinja2",
                function_states=["angle", "angular_velocity"],
                function_args=["length", "gravity"],
                required_imports=["import numpy as np"]
            ),
            "MassSpringOscillation" :
            DynamicalSystemFunction(
                function_name="MassSpringOscillation",
                function_descriptors=[
                    "A mass-spring system consists of a mass attached to a spring. The spring exerts a restoring force proportional to the displacement from its equilibrium position. The motion is periodic and can be modeled as simple harmonic motion. The period of oscillation depends on the mass and the spring constant."
                ],
                function_body_template="mass_spring_oscillation.jinja2",
                function_states=["displacement", "velocity"],
                function_args=["mass", "spring_constant", "previous_displacement", "previous_velocity", "time_step"],
                required_imports=["import numpy as np"]
            )

        }

        self.function_descriptors_to_function_dict = {}

        for function in self.dynamical_function_dict.values():
            for descriptor in function.function_descriptors:
                self.function_descriptors_to_function_dict[descriptor] = function.function_name

# def generate_function_parameters(function_args_to_retain: list[str]):
#     function_parameters = function_args_to_retain.copy()
#     # for function in dynamical_function_dict.values():
#     #     for arg in function.function_args:
#     #         if arg not in function_parameters:
#     #             function_parameters.append(arg)
#     stringified_function_parameters = ", ".join(function_parameters)
#     return stringified_function_parameters

    def match_args(self, arg, class_attributes, surrounding_numeric_attributes):
        for category, attributes in class_attributes.items():
            if category.lower() == arg.lower():
                return f"self.{attributes}"
        print("surrounding_numeric_attributes", surrounding_numeric_attributes)
        for system_component, categories in surrounding_numeric_attributes.items():
            print("categories", categories)
            for category in categories:
                if category.lower() == arg.lower():
                    system_component = system_component.title()
                    return f"{system_component}.{category}"
        return 1 # default value

    def generate_simulate_function(self, function_name: str, function_states: list[str]):
        simulate_template = self.function_edit_env.get_template("simulate_template.jinja2")
        function_arguments = [f"self.{state}" for state in function_states]
        function_arguments_str = ", ".join(function_arguments)
        return simulate_template.render({
            "function_name": function_name,
            "function_arguments": function_arguments_str,
        })



    def guess_function(self,
                           function_name: str,
                           class_attributes: dict[str, str],
                           surrounding_numeric_attributes: dict[str, str],
                           function_prompt: str):
        function_descs_to_check = self.function_descriptors_to_function_dict.keys()
        tokenized_function_prompt = self.nlp(function_prompt)
        current_max_similarity = 0
        current_guessed_function_name = None
        matched_system_components = []
        for function_descriptor in function_descs_to_check:
            similarity_score = tokenized_function_prompt.similarity(self.nlp(function_descriptor))
            if similarity_score > current_max_similarity:
                current_max_similarity = similarity_score
                current_guessed_function_name = self.function_descriptors_to_function_dict[function_descriptor]
        if current_guessed_function_name is not None and current_max_similarity > 0.79:
            print(f"Guessed function name: {current_guessed_function_name}")
            print(f"Similarity score: {current_max_similarity}")
            dynamical_system_function = self.dynamical_function_dict[current_guessed_function_name]
            function_template = self.env.get_template(dynamical_system_function.function_body_template)

            render_dict = {
                "function_name": function_name,
                "function_prompt": function_prompt,
            }

            for arg in dynamical_system_function.function_args:
                if arg in self.constant_dict:
                    render_dict[arg] = self.constant_dict[arg]
                else:
                    matched_arg = self.match_args(arg, class_attributes, surrounding_numeric_attributes)
                    render_dict[arg] = matched_arg
                    matched_system_component = matched_arg.split(".")[0]
                    if matched_system_component not in matched_system_components:
                        matched_system_components.append(matched_system_component)
            function_implementation = function_template.render(render_dict)

            initial_states = [ f"initial_{state}" for state in dynamical_system_function.function_states]
            new_init_interface = f"def __init__(self, {', '.join(initial_states)}):\n"
            return GuessFunctionResult(function_implementation=function_implementation,
                                    function_states=dynamical_system_function.function_states,
                                    new_init_interface=new_init_interface,
                                    simulate_function=self.generate_simulate_function(function_name, dynamical_system_function.function_states),
                                    required_imports=dynamical_system_function.required_imports,
                                    matched_system_components=matched_system_components,
                                    )
        else:
            return None
                                   
    


# guess_function_result = guess_function(
#     function_name="CanBeApproximated",
#     function_args_to_retain=["self"],
#     ClassName="Motion",
#     function_prompt="Gravity causes the pendulum to swing .The motion is periodic and can be approximated by simple harmonic motion for small angles .The pendulum 's period depends on period length and gravity .",
#     class_attributes={"Type": "periodic", "Approximation": "simple harmonic", "Condition": "small angles", "Angle": "small"},
#     surrounding_numeric_attributes={"Bob": "weight" , "String": "Length"},
# )

# print(guess_function_result.function_implementation)

# print(guess_function_result.new_init_interface)

# print(guess_function_result.init_append)