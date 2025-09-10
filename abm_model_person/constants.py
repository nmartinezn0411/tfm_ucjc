'''
constants.py 
En este archivo se definen todas las constantes que existen en el proyecto.
Estas constantes se encuentran explicadas en la documnetación del proyecto.

Se debe tomar en cuenta que cada 100 pixeles son 5 metros
'''
WIDTH, HEIGHT = 1800, 1000
# last position y for all lines
FINAL_Y = 800  

# Person features
GROUP_SIZE = 1                   # Number of people per group 
INFECTION_RATE = 0.15 # % de las personas estarán infectadas
ASYMPTOMATIC_RATE = 0.4 # % de las personas serán asintómaticas

# Mask use
MASK_USE = 0.8 # Percentage of people using it
MASK_REDUCE = (0.6, 0.8) # Reduction by the mask use

# Temperature test precision
TEMP_DETEC = 0.4 # Percentage of people that the test will detect

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255) 
YELLOW = (255, 255, 0)