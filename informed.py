import math
import heapq

def haversine(coord1, coord2):
    """
    Calculate the great-circle distance between two points
    on the Earth's surface in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers
    
    lat1, lon1 = math.radians(coord1["lat"]), math.radians(coord1["lon"])
    lat2, lon2 = math.radians(coord2["lat"]), math.radians(coord2["lon"])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

#Greedy Best-First Search
def greedy_best_first(graph, locations, start, goal):
    """
    Greedy Best-First Search
    Returns: {"path": list, "expanded": list, "distance": float}
    """
    if start not in locations or goal not in locations:
        return {"path": None, "expanded": [], "distance": 0.0}
        
    goal_coord = locations[goal]
    
    pq = []
    # Entry: (heuristic, counter, node, path, path_cost)
    counter = 0
    h_start = haversine(locations[start], goal_coord)
    heapq.heappush(pq, (h_start, counter, start, [start], 0.0))
    
    visited = set()
    expanded = []
    
    while pq:
        _, _, node, path, cost = heapq.heappop(pq)
        
        if node in visited:
            continue
            
        visited.add(node)
        expanded.append(node)
        
        if node == goal:
            return {"path": path, "expanded": expanded, "distance": round(cost, 2)}
            
        neighbors = sorted(graph.get(node, {}).items(), key=lambda x: x[0])
        for neighbor_name, neighbor_distance in neighbors:
            if neighbor_name not in visited:
                counter += 1
                h_val = haversine(locations[neighbor_name], goal_coord)
                heapq.heappush(pq, (h_val, counter, neighbor_name, path + [neighbor_name], cost + neighbor_distance))
                
    return {"path": None, "expanded": expanded, "distance": 0.0}

#A* Search
def a_star(graph, locations, start, goal):
    """
    A* Search
    Returns: {"path": list, "expanded": list, "distance": float}
    """
    if start not in locations or goal not in locations:
        return {"path": None, "expanded": [], "distance": 0.0}
        
    goal_coord = locations[goal]
    
    pq = []
    # Entry: (f_cost, counter, node, path, g_cost)
    counter = 0
    h_start = haversine(locations[start], goal_coord)
    heapq.heappush(pq, (h_start, counter, start, [start], 0.0))
    
    visited = set()
    expanded = []
    
    while pq:
        f_cost, _, node, path, g_cost = heapq.heappop(pq)
        
        if node in visited:
            continue
            
        visited.add(node)
        expanded.append(node)
        
        if node == goal:
            return {"path": path, "expanded": expanded, "distance": round(g_cost, 2)}
            
        neighbors = sorted(graph.get(node, {}).items(), key=lambda x: x[0])
        for neighbor_name, neighbor_distance in neighbors:
            if neighbor_name not in visited:
                counter += 1
                g_new = g_cost + neighbor_distance
                h_val = haversine(locations[neighbor_name], goal_coord)
                f_new = g_new + h_val
                heapq.heappush(pq, (f_new, counter, neighbor_name, path + [neighbor_name], g_new))
                
    return {"path": None, "expanded": expanded, "distance": 0.0}