import time
import numpy as np
from vl53l5cx.vl53l5cx import VL53L5CX
import matplotlib.pyplot as plt
import math

def plot_graph(ax, x, y):
    
    ax.clear()
    ax.plot(x, y, 'o', label='Target')
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_title('Triangulated Position')
    ax.legend()
    ax.grid(True)

def find_third_vertex(A, B):
    # Known Verticies
    x1, y1 = 0, 0
    x2, y2 = 100, 0

    # Base
    C = 940

    # Using the law of cosines to find the angle between A and C
    # cos(?) = (A^2 + C^2 - B^2) / (2 * A * C)
    cos_theta = (A**2 + C**2 - B**2) / (2 * A * C)
    
    # Float error fix
    cos_theta = min(1, max(-1, cos_theta))
    
    theta = math.acos(cos_theta)

    # new coordinates
    x3 = int(x1 + A * math.cos(theta))
    y3 = int(y1 + A * math.sin(theta))

    return (x3, y3)

driver = VL53L5CX()
driver2 = VL53L5CX(bus_id=0)

alive = driver.is_alive()
if not alive:
    raise IOError("VL53L5CX Device is not alive")

print("Initialising...")
t = time.time()

driver2.init ()
driver.init()

print(f"Initialised ({time.time() - t:.1f}s)")

driver.set_ranging_frequency_hz(60)
driver2.set_ranging_frequency_hz(60)

# Ranging:
driver.start_ranging()
driver2.start_ranging()

previous_time = 0
loop = 0
array = np.zeros((4, 4), dtype=int)
array2 = np.zeros((4, 4), dtype=int)

plt.ion()
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))  # Create three subplots

heatmap1 = ax1.imshow(array, cmap='viridis', interpolation='none')
fig.colorbar(heatmap1, ax=ax1)
ax1.set_title('Heatmap of Sensor 1')

heatmap2 = ax2.imshow(array2, cmap='plasma', interpolation='none')
fig.colorbar(heatmap2, ax=ax2)
ax2.set_title('Heatmap of Sensor 2')

sensor1 = 0
sensor2 = 0

for j in range(10):
    if driver.check_data_ready():
        ranging_data = driver.get_ranging_data()
        ranging_data2 = driver2.get_ranging_data()

        for i in range(16):
            
            row = i // 4
            col = i % 4
           
            array[row, col] = ranging_data.distance_mm[driver.nb_target_per_zone * i]
      
            array2[row, col] = ranging_data2.distance_mm[driver.nb_target_per_zone * i]

        sensor1 = min(array[3, 0], array[2,1], array[1, 2], array[0, 3])
        sensor2 = min(array[3, 0], array2[2,1], array2[1, 2], array2[0, 3])
        
        finalX, finalY = find_third_vertex(sensor1, sensor2)
     
        print(finalX, finalY)
        
        plot_graph(ax3, finalX, finalY)
        heatmap1 = ax1.imshow(array)
        heatmap2 = ax2.imshow(array2)
        
        plt.draw()
        plt.pause(0.001)
        

        loop += 1



