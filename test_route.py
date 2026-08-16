from route_planner import get_shed_coordinates, manhattan_distance, generate_movement_actions

# Test shed coordinates
print("Shed coordinates:", get_shed_coordinates())

# Test distance
print("Distance (4,4) to (6,5):", manhattan_distance((4,4), (6,5)))

# Test movement
print("Moves from (4,4) to (6,5):", generate_movement_actions((4,4), (6,5)))