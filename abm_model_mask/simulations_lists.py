import numpy as np

WIDTH, HEIGHT = 1800, 1000

# Define the initial path waypoints 
'''These are the entries of the space that we are analyzing'''
initial_path_waypoints = [
   # np.array([100, 800]), Position at the beggining
    np.array([100, 100]),
]

# Define the final path waypoints 
'''These are the exits of the space that we are analyzing'''
final_path_waypoints = [
    np.array([350, 600]),
    np.array([700, 600]),
    np.array([1100, 600]),
    np.array([1600, 600]),
]

# Define path waypoints (green)
middle_path_waypoints = [# 975 is the midle point of the market
                         
    np.array([600, 80]),
    np.array([850, 80]),
    np.array([1100, 80]),
    np.array([1350, 80]),
    
    np.array([600, 100]),
    np.array([850, 100]),
    np.array([1100, 100]),
    np.array([1350, 100]),
    
    np.array([600, 120]),
    np.array([850, 120]),
    np.array([1100, 120]),
    np.array([1350, 120]),
    
    np.array([600, 180]),
    np.array([850, 180]),
    np.array([1100, 180]),
    np.array([1350, 180]),
    
    np.array([600, 200]),
    np.array([850, 200]),
    np.array([1100, 200]),
    np.array([1350, 200]),
    
    np.array([600, 220]),
    np.array([850, 220]),
    np.array([1100, 220]),
    np.array([1350, 220]),
    
    np.array([600, 280]),
    np.array([850, 280]),
    np.array([1100, 280]),
    np.array([1350, 280]),

    np.array([600, 300]),
    np.array([850, 300]),
    np.array([1100, 300]),
    np.array([1350, 300]),
    
    np.array([600, 320]),
    np.array([850, 320]),
    np.array([1100, 320]),
    np.array([1350, 320]),
    
    np.array([600, 380]),
    np.array([850, 380]),
    np.array([1100, 380]),
    np.array([1350, 380]),

    np.array([600, 400]),
    np.array([850, 400]),
    np.array([1100, 400]),
    np.array([1350, 400]),
    
    np.array([600, 420]),
    np.array([850, 420]),
    np.array([1100, 420]),
    np.array([1350, 420]),
    
    np.array([600, 480]),
    np.array([850, 480]),
    np.array([1100, 480]),
    np.array([1350, 480]),

    np.array([600, 500]),
    np.array([850, 500]),
    np.array([1100, 500]),
    np.array([1350, 500]),
    
    np.array([600, 520]),
    np.array([850, 520]),
    np.array([1100, 520]),
    np.array([1350, 520]),
    
    np.array([600, 580]),
    np.array([850, 580]),
    np.array([1100, 580]),
    np.array([1350, 580]),

    np.array([600, 600]),
    np.array([850, 600]),
    np.array([1100, 600]),
    np.array([1350, 600]),
]

# Define the exit path waypoints, these are the exit path that each agent will follow after the checkout process
exit_waypoints = {
    # First positions of the exit
    'exit1': [
        np.array([1600, 880]),
        np.array([1640, 880]),
    ],
    # Lasts positions of the exit
    'exit2': [
        np.array([1600, 910]),
        np.array([1640, 930]),
    ]
}

checkout_map = {
    "F1": [
        [350, 650, -1], 
        [350, 700, -1], 
        [350, 750, -1],        
        [350, 800, -1],        
    ],
    "F2": [
        [470, 650, -1], 
        [470, 700, -1], 
        [470, 750, -1],        
        [470, 800, -1],        
    ],
    "F3": [
        [600, 650, -1], 
        [600, 700, -1], 
        [600, 750, -1],        
        [600, 800, -1],        
    ],
    "F4": [
        [720, 650, -1], 
        [720, 700, -1], 
        [720, 750, -1],        
        [720, 800, -1],        
    ],
    "F5": [
        [850, 650, -1], 
        [850, 700, -1], 
        [850, 750, -1],        
        [850, 800, -1],        
    ],
    "F6": [
        [970, 650, -1], 
        [970, 700, -1], 
        [970, 750, -1],        
        [970, 800, -1],        
    ],
    "F7": [
        [1100, 650, -1], 
        [1100, 700, -1], 
        [1100, 750, -1],        
        [1100, 800, -1],        
    ],
    "F8": [
        [1220, 650, -1], 
        [1220, 700, -1], 
        [1220, 750, -1],        
        [1220, 800, -1],        
    ],
    "F9": [
        [1350, 650, -1], 
        [1350, 700, -1], 
        [1350, 750, -1],        
        [1350, 800, -1],        
    ],
    "F10": [
        [1470, 650, -1], 
        [1470, 700, -1], 
        [1470, 750, -1],        
        [1470, 800, -1],        
    ],
    "F11": [
        [1600, 650, -1], 
        [1600, 700, -1], 
        [1600, 750, -1],        
        [1600, 800, -1], 
    ],
}

# Define walls (black - solid, must avoid)
walls = [# A vector is define like this [x1, y1, x2, y2]
    # Screen boundaries
    [0, 0, WIDTH, 0],        # Top wall
    [WIDTH, 0, WIDTH, HEIGHT],  # Right wall
    [WIDTH, HEIGHT, 0, HEIGHT],  # Bottom wall
    [0, HEIGHT, 0, 0],        # Left wall
    
    # Interior walls with passages
    [200, 50, 1700, 50], # top wall market
    [1700, 50, 1700, 900], # right wall market
    [1550, 900, 200, 900], # botton wall market
    [200, 900, 200, 150], # left wall market
    
    # Pasillos
    [400, 150, 1500, 150], # division 1
    [400, 250, 1500, 250], # division 2
    [400, 350, 1500, 350], # division 3
    [400, 450, 1500, 450], # division 4
    [400, 550, 1500, 550], # division 5
]