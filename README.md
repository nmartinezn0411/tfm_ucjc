# Archivo README del TFM de Nelson Martínez.

### DESARROLLO DE UN MODELO BASADO EN AGENTES PARA LA SIMULACIÓN DE LA PROPAGACIÓN DE ENFERMEDADES INFECCIOSAS EN EVENTOS CONTROLADOS: EVALUACIÓN DE INTERVENCIONES EN SUPERMERCADOS DURANTE LA EPIDEMIA DEL COVID - 19

Este archivo busca aclarar el uso de este repositorio para poder ejemplificar las simulaciones realizadas en este, de esta manera investigadores del tema podrán apoyarse de este proyecto para realizar trabajos basados en lo que se expone aquí.

### 1. Instalación de librerías

Para instalar las librerías utilizadas en este proyecto es necesario instalar las librerías que se definen en el archivo requirements.txt con el comando:

pip install -r requirements.txt

De esta manera todas las librerías usadas en el proyecto podrán ser instaladas en el entorno que se está ejemplificando el proyeto.

### 2. Estrucutura del proyecto

En esta sección se estará explicando la estructura de los archivos del proyecto.

- database_test.ipynb: A partir de este notebook se pueden crear las tablas utilizadas en el proyecto, para este proyecto en específico se está utilizando el gestor de base de datos de PostgreSQL junto a la herramienta de sqlalchemy, para el manejo más sencillo de los datos se está utilizando la interfaz de PGadmin, aunque esta herramienta no es necesaria para el manejo de los datos, hace que algunas tareas sean más sencillas.

Este archivo contiene todas las clases que definen las tablas que tiene la base de datos del proyecto, también contiene la función save_simulation_run, la cual se exporta en el archivo principal run.py de cada tipo de simulación, esta función permite guardar la información recopilada por cada simulación corrida. 

- requirements.txt: Como se había explicado anteriormente, este archivo contiene una lista de todas las librerías utilizadas para el desarrollo del proyecto.

- simulation.txt: Este archivo contiene una lista de algunos de los aspectos utilizados para correr la simulación, en la documentación del proyecto se explica más a detalle todos los aspectos utilizados para la simulación y las investigaciones que respaldan el uso de las variables/constantes utilizadas.

- prueba.ipynb: En este archivo se fueron realizando pruebas hasta tener la primer versión del proyecto, cualquier usuario desarrollador puede así mismo realizar todas pruebas que desee del código que tiene el proyecto.

- historial_changes.ipynb: Este archivo contiene el historial de cambios que ha tenido el proyecto, aunque el repositorio guarda los commits realizados, se guardan todas las versiones que ha tenido la simulación para la realzar pruebas rápidas cuando sea necesario.

- abm_model: Esta carpeta contiene todos los archivos utilizados para el primer tipo de simulación del proyecto, este tipo de simulación no tiene ningún tipo de intervención no farmaceútica.

- abm_model_mask: Esta carpeta contiene los archivos utilizados para el segundo tipo de simulación, en donde se implementa el uso de mascarilla en la población de agentes utilizadas.

- abm_model_person: Esta carpeta contiene los archivos utilizados para el tercer tipo de simulación, en este tipo de simulación también se implementa la toma de temperatura, se limita aún más la cantidad de agentes en el ambiente, entran con un tiempo de espera más elevado, y hay menor cantidad de filas de espera.

### 3. Estructura de los archivos de los modelos

Cada uno de los modelos tiene poco cambios en los archivos, se pudo haber realizado una sola carpeta y colocar cada uno de los cambios según condicionales, pero para dividir mejor aún cada tipo de simulación cuidando no hacer ningún tipo de cambio accidentado, se decidió crear 3 carpetas. A continuación se estará explicando cada uno de los archivos que se encuentran en las carpetas de los tipos de simulaciones.

- constants.py: En este archivo se definen las contantes globales del proyecto, estos son los colores que se utilizan en la simulación, las dimensiones del ambiente, y variables epidemicas que pueden cambiar según el modelo.

- database_configuration.py: Este archivo es similar al de de database_tests.ipynb, de aquí se utiliza la función de save_simulation_run para guardar los datos generados por la corrida de una simulación.

- functions.py: Este programa tiene diferentes funciones las cuales se utilizan en el desarrollo del proyecto. En una sección posterior se hablará de manera más detallada de estas funciones. 

- person_class.py: Aquí se define la clase Person, que es la que maneja toda la lógica detrás del movimiento de las personas. Más adelante se hablará con mayor profundidad de esta clase.

- pruebas.ipynb: Notebook para realizar pruebas con las funciones. 

- run.py: En este archivo se encuentra la lógica general de la simulación y es de donde se llaman todas las otras funciones/clases para que el proyecto funcione.

- simulations_lists.py: Aquí se encuentra todas las listas que se utilizan en el proyecto. 

### 4. Funciones del archivo functions.py

En esta sección se explicará de manera superfecial el propósito de todas las funciones que se encuentran en el archivo functions.py.

- get_checkout_time: se utiuliza para generar un tiempo estimado de que tiempo durará la persona en el checkout del supermercado.

- generate_random_path: se utiliza para generar el camino aleatorio que la persona estará siguiendo hasta llegar al proceso de compra.

- exit_path_creation: elige de manera aleatoria el camino que seguirá la persona en la salida.

- best_slot: según la cantidad de posiciones vacias, un cliente elige el puesto ideal.

- register_person: Se registra una persona en el checkout_map.

- unregister_person: Se elimina una persona del checkout_map.

- find_line_and_idx_by_coords: Nos ayuda a llevar conteo de la cantidad de personas en una línea. 

- try_advance_in_line: Para mover hacia delante cada vez que tenga la oportunidad

- round_down: Redondea al valor de 10 más cercano, esto se utiliza para el mapa de puntos de exposición.

- draw_logic: Dibuja toda la simulación.

- reset_checkout_map: Cuando acaba una simulación, hace que toda el checkout mapa se encuentre como vacio de nuevo. 

### 5. Clase Person

En esta sección se encuentra explicada las variables y los métodos que se utiliza para la Clase Person en el proyecto, que es clase que define a cada una de las instancias agentes que estarán protagonizando el proyecto. 

- __init__: El método de inicialización de una instancia define todas las variables iniciales que tiene un agente, donde aparece inicialmente, si es una persona infectada, si en ese momento en la simulación se encuentra esperando, el tiempo que durará en la salida, la velocidad con la que estará anando en la simulación, entre otras cosas más.

- follow_path: En este método se encuentra la lógica que utiliza la persona para seguir todos los puntos a los cuales se estará movimiendo en la simulación, desde que la persona entra a la simulación, hasta que sale de la misma después de acabar el proceso de pago de productos.

- update: Este método ayuda a actualizar la posición del agente según el entorno donde se encuentra, tomando en cuenta el modelo de fuerzas sociales y los objetivos que tiene en el momento.

- distance_to_wall: Calcula la distancia que tiene con las paredes de la simulación.

- draw: Dibuja al agente en la simulación y muestra el radio de infección como un radio pulsante alrededor de una persona infectada. 

### 6. simulations_lists.py

En esta sección se estará explicando las listas que se utilizan en la simulación, estas listas definen lugares clave de la simulación, que en la mayoría de los casos definen el espacio físico de la simulación.

- initial_path_waypoints: Este es el punto de entrada de la simulación.

- final_path_waypoints: Define los puntos finales en el cual el agente puede acabar el recorrido en el super y pasar al proceso de compra.

- middle_path_waypoints: Define los puntos en donde existen productos y la persona puede tomarlos.

- exit_waypoints: una de las dos salidas que las personas pueden tener al momento de salir. 

- checkout_map: Mapa que nos muestra el sistema de filas en el supermercado, dígase como están ocupadas las filas y cuales son las líneas que definen las filas.

- walls: Define las dimensiones de las paredes.

### 7. Realización de pruebas

Cada archivo run.py por defecto tiene que la simulación corra tan rápido como el computador en donde esté corriendo lo permita, esta configuración se puede cambiar descomentando esta línea:
#dt = clock.tick(TARGET_FPS) / 1000.0  # real-time pacing
, de esta manera la simulación estará corriendo segundo a segundo como en la vida real. Si se coloa la variable FAST_MODE a True la simulación estará corriendo tan rápido como sea posible, quitando de esta manera la pantalla de PyGame en donde está corriendo el proyecto. 

Para correr el proyecto solo se debe entrar a la carpeta del modelo que se desea y correr el siguiente comando:

python run.py 

### 8. Video de la simulación.

El siguiente video muestra un ejemplo de la simulación normal con 40 agentes.

https://youtu.be/M9vuGYWxO0Q?si=QIJkCcYsZ2NbRS8v

### 9. Equipo con el cual se realizó el proyecto. 

El sistema operativo con el cual fue realizado este proyecto es el siguiente, este comanod fue realizado usanod el comnado de linux neofetch:


```bash

            .-/+oossssoo+/-.               
        `:+ssssssssssssssssss+:`           --------------- 
      -+ssssssssssssssssssyyssss+-         OS: Ubuntu 22.04.5 LTS x86_64 
    .ossssssssssssssssssdMMMNysssso.       Host: 82K2 IdeaPad Gaming 3 15ACH6 
   /ssssssssssshdmmNNmmyNMMMMhssssss/      Kernel: 6.8.0-78-generic 
  +ssssssssshmydMMMMMMMNddddyssssssss+     Uptime: 12 mins 
 /sssssssshNMMMyhhyyyyhmNMMMNhssssssss/    Packages: 2779 (dpkg), 6 (flatpak),  
.ssssssssdMMMNhsssssssssshNMMMdssssssss.   Shell: bash 5.1.16 
+sssshhhyNMMNyssssssssssssyNMMMysssssss+   Resolution: 1920x1080, 2560x1440 
ossyNMMMNyMMhsssssssssssssshmmmhssssssso   DE: GNOME 42.9 
ossyNMMMNyMMhsssssssssssssshmmmhssssssso   WM: Mutter 
+sssshhhyNMMNyssssssssssssyNMMMysssssss+   WM Theme: Adwaita 
.ssssssssdMMMNhsssssssssshNMMMdssssssss.   Theme: Yaru-dark [GTK2/3] 
 /sssssssshNMMMyhhyyyyhdNMMMNhssssssss/    Icons: Yaru [GTK2/3] 
  +sssssssssdmydMMMMMMMMddddyssssssss+     Terminal: gnome-terminal 
   /ssssssssssshdmNNNNmyNMMMMhssssss/      CPU: AMD Ryzen 5 5600H with Radeon G 
    .ossssssssssssssssssdMMMNysssso.       GPU: NVIDIA GeForce RTX 3050 Ti Mobi 
      -+sssssssssssssssssyyyssss+-         GPU: AMD ATI 06:00.0 Cezanne 
        `:+ssssssssssssssssss+:`           Memory: 4620MiB / 13824MiB 
            .-/+oossssoo+/-.
                                                                   
                                                                   
