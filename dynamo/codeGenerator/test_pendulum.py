import numpy as np

import matplotlib.pyplot as plt

def simulate_pendulum(theta0, length, g, time_step, total_time):
    """
    Simulates the angle of a simple pendulum over time.

    Parameters:
        theta0 (float): Initial angle (in radians).
        length (float): Length of the pendulum (in meters).
        g (float): Acceleration due to gravity (in m/s^2).
        time_step (float): Time step for the simulation (in seconds).
        total_time (float): Total simulation time (in seconds).

    Returns:
        t (numpy.ndarray): Array of time values.
        theta (numpy.ndarray): Array of angle values over time.
    """
    # Number of time steps
    num_steps = int(total_time / time_step)
    
    # Initialize arrays for time and angle
    t = np.linspace(0, total_time, num_steps)
    theta = np.zeros(num_steps)
    
    # Initial conditions
    theta[0] = theta0
    omega = 0  # Initial angular velocity
    
    # Time-stepping simulation using Euler's method
    for i in range(1, num_steps):
        alpha = -(g / length) * np.sin(theta[i - 1])  # Angular acceleration
        omega += alpha * time_step  # Update angular velocity
        theta[i] = theta[i - 1] + omega * time_step  # Update angle
    
    return t, theta

# Example usage
if __name__ == "__main__":
    theta0 = np.radians(30)  # Initial angle in radians
    length = 1.0  # Length of pendulum in meters
    g = 9.81  # Acceleration due to gravity in m/s^2
    time_step = 0.01  # Time step in seconds
    total_time = 10  # Total simulation time in seconds

    t, theta = simulate_pendulum(theta0, length, g, time_step, total_time)

    # Plot the results
    plt.plot(t, np.degrees(theta))
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (degrees)")
    plt.title("Simple Pendulum Simulation")
    plt.grid()
    plt.savefig("pendulum_simulation.png")