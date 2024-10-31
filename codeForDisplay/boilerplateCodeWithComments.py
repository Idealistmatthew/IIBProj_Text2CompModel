class Engine:
    """
    The Engine class represents a basic engine with an ignitor, heat capacity, weight, and cost.
    """

    def __init__(self):
        """
        Initializes the Engine with default values for ignitor, heat capacity, weight, and cost.
        """
        self.ignitor = Ignitor()
        self.heat_capacity = 300   # J/kg*K
        self.weight = 1000 # kg
        self.cost = 1000 # USD
    
    def start(self):
        """
        Starts the engine. This method would likely involve engaging the ignitor and initiating
        the combustion process, which in turn would generate power. The specifics of how the 
        engine starts would depend on the type of engine and its design.
        """
        pass

    def stop(self):
        """
        Stops the engine. This method would probably involve cutting off the fuel supply and 
        disengaging the ignitor, leading to a cessation of the combustion process and a gradual 
        decrease in power output. The exact mechanism would vary based on the engine's design.
        """
        pass