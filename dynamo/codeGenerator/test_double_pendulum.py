import numpy as np

import matplotlib.pyplot as plt

def simulate_double_pendulum(theta1_0, theta2_0, length1, length2, mass1, mass2, g, time_step, total_time):
    """
    Simulates the motion of a double pendulum over time.

    Parameters:
        theta1_0 (float): Initial angle of the first pendulum (in radians).
        theta2_0 (float): Initial angle of the second pendulum (in radians).
        length1 (float): Length of the first pendulum (in meters).
        length2 (float): Length of the second pendulum (in meters).
        mass1 (float): Mass of the first pendulum (in kg).
        mass2 (float): Mass of the second pendulum (in kg).
        g (float): Acceleration due to gravity (in m/s^2).
        time_step (float): Time step for the simulation (in seconds).
        total_time (float): Total simulation time (in seconds).

    Returns:
        t (numpy.ndarray): Array of time values.
        theta1 (numpy.ndarray): Array of angle values for the first pendulum over time.
        theta2 (numpy.ndarray): Array of angle values for the second pendulum over time.
    """
    # Number of time steps
    num_steps = int(total_time / time_step)
    
    # Initialize arrays for time and angles
    t = np.linspace(0, total_time, num_steps)
    theta1 = np.zeros(num_steps)
    theta2 = np.zeros(num_steps)
    
    # Initial conditions
    theta1[0] = theta1_0
    theta2[0] = theta2_0
    omega1 = 0  # Initial angular velocity of the first pendulum
    omega2 = 0  # Initial angular velocity of the second pendulum
    
    # Time-stepping simulation using Euler's method
    for i in range(1, num_steps):
        # Calculate angular accelerations using the equations of motion
        delta_theta = theta1[i - 1] - theta2[i - 1]
        denom1 = (2 * mass1 + mass2 - mass2 * np.cos(2 * delta_theta))
        denom2 = (length2 / length1) * denom1
        
        alpha1 = (-g * (2 * mass1 + mass2) * np.sin(theta1[i - 1]) -
                  mass2 * g * np.sin(theta1[i - 1] - 2 * theta2[i - 1]) -
                  2 * np.sin(delta_theta) * mass2 *
                  (omega2**2 * length2 + omega1**2 * length1 * np.cos(delta_theta))) / (length1 * denom1)
        
        alpha2 = (2 * np.sin(delta_theta) *
                  (omega1**2 * length1 * (mass1 + mass2) +
                   g * (mass1 + mass2) * np.cos(theta1[i - 1]) +
                   omega2**2 * length2 * mass2 * np.cos(delta_theta))) / (length2 * denom2)
        
        # Update angular velocities
        omega1 += alpha1 * time_step
        omega2 += alpha2 * time_step
        
        # Update angles
        theta1[i] = theta1[i - 1] + omega1 * time_step
        theta2[i] = theta2[i - 1] + omega2 * time_step
    
    return t, theta1, theta2

# Example usage
if __name__ == "__main__":
    theta1_0 = np.radians(120)  # Initial angle of the first pendulum in radians
    theta2_0 = np.radians(-10)  # Initial angle of the second pendulum in radians
    length1 = 1.0  # Length of the first pendulum in meters
    length2 = 1.0  # Length of the second pendulum in meters
    mass1 = 1.0  # Mass of the first pendulum in kg
    mass2 = 1.0  # Mass of the second pendulum in kg
    g = 9.81  # Acceleration due to gravity in m/s^2
    time_step = 0.01  # Time step in seconds
    total_time = 20  # Total simulation time in seconds

    t, theta1, theta2 = simulate_double_pendulum(theta1_0, theta2_0, length1, length2, mass1, mass2, g, time_step, total_time)

    # Plot the results
    plt.plot(t, np.degrees(theta1), label="Pendulum 1")
    plt.plot(t, np.degrees(theta2), label="Pendulum 2")
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (degrees)")
    plt.title("Double Pendulum Simulation")
    plt.legend()
    plt.grid()
    plt.savefig("double_pendulum_simulation.png")