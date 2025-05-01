import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docplex.mp.model import Model

# coordinates in a list

data = pd.read_excel("georef-united-states-of-america-zc-point.xlsx")

coordinates = [[float(s) for s in x.split(",")] for x in (data["Geo Point"].values)]


# Convert to numpy array for easier manipulation
coords_array = np.array(coordinates)

# Find the bottom-left-most point (minimum latitude and minimum longitude)
origin = np.min(coords_array, axis=0)

# Normalize the coordinates by subtracting the origin
normalized_coords = coords_array - origin

#Scale the coordinates`
scaled_latitudes = normalized_coords[:, 0] * 10000
scaled_longitudes = normalized_coords[:, 1] * 10

# Define grid cell size
grid_x_size = 1  # Longitude increments by single digits
grid_y_size = 1000  # Latitude increments by 1000

# Compute grid cell assignments and labels
grid_cells = []
city_grid_mapping = {}
grid_cell_counts = {}
for i, (lon, lat) in enumerate(zip(scaled_longitudes, scaled_latitudes), start = 1):
    # Find bottom-left corner of the grid cell
    cell_x = (lon // grid_x_size) * grid_x_size
    cell_y = (lat // grid_y_size) * grid_y_size
    grid_label = int(cell_x + cell_y ) # Sum of bottom-left x and y
    grid_cells.append((cell_x, cell_y, grid_label))

    # Store in dictionary
    city_grid_mapping[i] = grid_label

    if grid_label in grid_cell_counts:
        grid_cell_counts[grid_label] += 1
    else:
        grid_cell_counts[grid_label] = 1

for i in grid_cell_counts:
    if grid_cell_counts[i] != 1:
        print(grid_cell_counts[i])

# Create the figure and plot points
plt.figure(figsize=(8, 6))
plt.scatter(scaled_longitudes, scaled_latitudes, marker='o', color='blue')

# Annotate points with grid cell labels
for i, (lon, lat, label) in enumerate(grid_cells):
    plt.text(lon, lat, f'Cell {label}', fontsize=12, verticalalignment='bottom', color='red')

# Set grid with increments of 1000 for latitude
plt.xticks(np.arange(0, np.max(scaled_longitudes) + 1, grid_x_size))  # Single-digit increments horizontally
plt.yticks(np.arange(0, np.max(scaled_latitudes) + grid_y_size, grid_y_size))  # Thousand increment vertically

# Labels and grid
plt.xlabel("Normalized Longitude (single-digit increments)")
plt.ylabel("Scaled Latitude (increments of 1000)")
plt.title("City Locations with Grid Cell Labels")
plt.grid(True)

# Show plot
plt.show()

print(city_grid_mapping)

# Define grid boundaries
max_x = int(np.max(scaled_longitudes))  # Max longitude (normalized)
max_y = int(np.max(scaled_latitudes))  # Max latitude (scaled by 1000)

# Define grid cell size
grid_x_size = 1  # Longitude increments by single digits
grid_y_size = 1000  # Latitude increments by 1000

grid_labels = []
# Iterate through every grid cell in the defined range
for x in range(0, max_x + 1, grid_x_size):  # Step through longitude values
    for y in range(0, max_y + grid_y_size, grid_y_size):  # Step through latitude values
        grid_label = x + y  # Sum of bottom-left x and y coordinates
        grid_labels.append(grid_label)
        print(f"Grid Cell ({x}, {y}) -> Label: {grid_label}")


# Initialize CPLEX model
mdl = Model(name="Mcdonalds_Problem")

# Define size index range
size = range(3)  # 0 to 2


# Create binary decision variables with indices (grid label, arbitrary index)
binary_variables = {(grid, k): mdl.binary_var(name=f"x_{grid}_{k}")
                    for grid in grid_labels for k in size}

for i in grid_labels:
    if i in grid_cells:
        mdl.add_constraint(mdl.sum(binary_variables[i,k] for k in range(3)) <= 1)
    else:
        mdl.add_constraint(mdl.sum(binary_variables[i,k] for k in range(3)) == 0)

#Size 2
for i in grid_cells:
    mdl.add_constraint()



# Print confirmation of variables created
print(f"Created {len(binary_variables)} binary decision variables.")

