from collections import deque
import heapq

#Breadth-First Search, taken from lab 2
def bfs(graph, start, goal):
    if start == goal:
        return {"path": [start], "expanded": [start], "distance": 0.0}
    
    queue = deque([(start, [start], 0.0)])
    visited = {start}
    expanded = []
    
    while queue:
        node, path, dist = queue.popleft()
        expanded.append(node)
        
        if node == goal:
            return {"path": path, "expanded": expanded, "distance": round(dist, 2)}
            
        # Sort neighbors alphabetically for deterministic tie-breaking
        neighbors = sorted(graph.get(node, {}).items(), key=lambda x: x[0])
        for neighbor_name, neighbor_distance in neighbors:
            if neighbor_name not in visited:
                visited.add(neighbor_name)
                queue.append((neighbor_name, path + [neighbor_name], dist + neighbor_distance))
                
    return {"path": None, "expanded": expanded, "distance": 0.0}


#Depth-First Search, taken from lab 2
def dfs(graph, start, goal):
    if start == goal:
        return {"path": [start], "expanded": [start], "distance": 0.0}
    
    stack = [(start, [start], 0.0)]
    visited = set()
    expanded = []
    
    while stack:
        node, path, dist = stack.pop()
        
        if node in visited:
            continue
            
        visited.add(node)
        expanded.append(node)
        
        if node == goal:
            return {"path": path, "expanded": expanded, "distance": round(dist, 2)}
            
        # Reverse sort neighbors so they are popped in alphabetical order
        neighbors = sorted(graph.get(node, {}).items(), key=lambda x: x[0], reverse=True)
        for neighbor_name, neighbor_distance in neighbors:
            if neighbor_name not in visited:
                stack.append((neighbor_name, path + [neighbor_name], dist + neighbor_distance))
                
    return {"path": None, "expanded": expanded, "distance": 0.0}

#Taken from lab 3
def ucs(graph, start, goal):
    pq = []
    # Entry: (cost, counter, node, path) to avoid comparisons on path list
    counter = 0
    heapq.heappush(pq, (0.0, counter, start, [start]))
    visited = set()
    expanded = []
    
    while pq:
        cost, _, node, path = heapq.heappop(pq)
        
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
                heapq.heappush(pq, (cost + neighbor_distance, counter, neighbor_name, path + [neighbor_name]))
                
    return {"path": None, "expanded": expanded, "distance": 0.0}

#IDS - taken from lab 3
def ids(graph, start, goal):
    """
    Iterative Deepening Search (IDS)
    Returns: {"path": list, "expanded": list, "distance": float}
    """
    expanded = []
    
    def dls(node, path, dist, limit, visited_path):
        expanded.append(node)
        if node == goal:
            return {"path": path, "distance": dist}
        if limit <= 0:
            return None
            
        neighbors = sorted(graph.get(node, {}).items(), key=lambda x: x[0])
        for neighbor_name, neighbor_distance in neighbors:
            if neighbor_name not in visited_path:
                res = dls(neighbor_name, path + [neighbor_name], dist + neighbor_distance, limit - 1, visited_path | {neighbor_name})
                if res is not None:
                    return res
        return None

    # Iteratively increase depth limit
    for limit in range(100):
        visited_path = {start}
        res = dls(start, [start], 0.0, limit, visited_path)
        if res is not None:
            res["expanded"] = expanded
            res["distance"] = round(res["distance"], 2)
            return res
            
    return {"path": None, "expanded": expanded, "distance": 0.0}