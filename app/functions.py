import psycopg2
from config import Config
from datetime import datetime

'''
Functions to interact with the database.
- execute_query(query): Executes a query in the database.
- insertar_bd(query): Inserts data into the database.
- obtener_lineas(): Retrieves all the lines.
- obtener_empleados_por_linea(): Retrieves the total number of employees per line.
- obtener_estaciones(linea): Retrieves all the stations of a line.
- obtener_empleados_por_estacion(linea): Retrieves the total number of employees per station of a line.
- registar_entrada_salida(user_id, linea, estacion, tipo, marca): Registers the entry or exit of an employee at a station.
- obtener_tipo_registro(user_id): Retrieves the most recent type of registration (Entry or Exit) for an employee.
- obtener_valores_salida(user_id): Retrieves the most recent line and station of exit for an employee.
- obtener_empleados_en_la_estacion(): Retrieves the employees who are in a station without having registered their exit.
- obtener_usuario(user_id): Retrieves the full name of a user based on their ID.
- obtener_imagen(user_id): Retrieves the image of a user based on their ID.
- get_line_id(linea): Retrieves the ID of a line based on its name.
'''

class Usuario:
    def __init__(self, numero_empleado, hora, linea):
        """
        Constructor de la clase Usuario.

        Args:
        - numero_empleado (int): Número de empleado.
        - hora (str): Hora.
        - linea (str): Línea.
        """
        self.numero_empleado = numero_empleado
        self.hora = hora
        self.linea = linea

    def set_numero_empleado(self, numero_empleado):
        """
        Establece el número de empleado.

        Args:
        - numero_empleado (int): Número de empleado.
        """
        self.numero_empleado = numero_empleado

    def set_hora(self, hora):
        """
        Establece la hora.

        Args:
        - hora (str): Hora.
        """
        self.hora = hora
    
    def set_linea(self, linea):
        """
        Establece la línea.

        Args:
        - linea (str): Línea.
        """
        self.linea = linea

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Usuario.

        Returns:
        - str: Representación en cadena del objeto Usuario.
        """
        return "Número de empleado: {}, Hora: {}, Línea: {}".format(self.numero_empleado, self.hora, self.linea)

def execute_query(query):
    """
    Ejecuta una consulta en la base de datos.

    Args:
    - query (str): Consulta SQL.

    Returns:
    - list: Resultados de la consulta.
    """
    # Establecer la conexión con la base de datos
    try:
        conn = psycopg2.connect(
            host=Config.DATABASE_HOST,
            user=Config.DATABASE_USER,
            database=Config.DATABASE_NAME,
            password=Config.DATABASE_PASSWORD,
            port=Config.DATABASE_PORT
        )
        # Resto del código de tu aplicación
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")

    print('Conexión establecida')

    # Crear un cursor para ejecutar consultas
    cursor = conn.cursor()

    # Ejecutar la consulta recibida como parámetro
    cursor.execute(query)

    # Obtener los resultados de la consulta
    results = cursor.fetchall()

    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()

    # Devolver los resultados de la consulta
    return results

def insertar_bd(query):
    """
    Inserta datos en la base de datos.

    Args:
    - query (str): Consulta SQL.
    """
    # Establecer la conexión con la base de datos
    conn = psycopg2.connect(
            host=Config.DATABASE_HOST,
            user=Config.DATABASE_USER,
            database=Config.DATABASE_NAME,
            password=Config.DATABASE_PASSWORD,
            port=Config.DATABASE_PORT
        )

    # Crear un cursor para ejecutar consultas
    cursor = conn.cursor()

    # Ejecutar la consulta recibida como parámetro
    cursor.execute(query)

    # Confirmar la transacción
    conn.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()

def get_lines():
    query = """
        SELECT *
        FROM lines
        ORDER BY CASE 
            WHEN name ~ '[0-9]' THEN CAST(SUBSTRING(name, '^[0-9]+') AS INTEGER)
            ELSE 0
        END DESC;
        """
    return execute_query(query)

def get_stations(line):
    query = """
        SELECT position_name,
            MAX(CASE WHEN side IN ('LH', 'BP') THEN employee_capacity END) AS employee_capacity_lh_or_bp,
            COALESCE(MAX(CASE WHEN side = 'RH' THEN employee_capacity END), 0) AS employee_capacity_rh
        FROM positions
        WHERE line_id = {}
        GROUP BY position_name
        ORDER BY position_name;
        """.format(line)
    return execute_query(query)

def get_employees_for_line(linea=None):
    """
    Obtiene el número total de empleados por línea.

    Args:
    - linea (str): Línea (opcional).

    Returns:
    - list: Resultados de la consulta.
    """
    if linea:
        query = """
        SELECT production_line, count(id_employee) AS employees_working
        FROM registers
        WHERE entry_hour IS NOT NULL and exit_hour is NULL AND
        production_line = '{}'
        GROUP BY production_line
        """.format(linea)
    else:
        query = """
        SELECT production_line, count(id_employee) AS employees_working
        FROM registers
        WHERE entry_hour IS NOT NULL and exit_hour is NULL
        GROUP BY production_line
        """
    return execute_query(query)

def get_employees_for_station(linea):
    """
    Obtiene el número total de empleados por estación de una línea.

    Args:
    - linea (str): Línea.

    Returns:
    - list: Resultados de la consulta.
    """
    query = """
    SELECT production_station, COUNT(*) AS empleados_trabajando
    FROM registers
    WHERE entry_hour IS NOT NULL AND exit_hour IS NULL AND
    production_line = '{}'
    GROUP BY production_station;
    """.format(linea)
    return execute_query(query)

def register_entry(user_id, linea, estacion, marca):
    """
    Registra la entrada de un empleado en una estación.

    Args:
        user_id (int): ID del empleado.
        linea (str): Línea.
        estacion (str): Estación.
        marca (str): Marca de tiempo.

    Returns:
        None
    """
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    query = "INSERT INTO registers (id_employee, date_register, production_line, production_station, entry_hour) VALUES ({}, '{}', '{}', '{}', '{}')".format(user_id, fecha_actual, linea, estacion, marca)
    insertar_bd(query)

def register_exit(user_id, marca):
    """
    Registra la salida de un empleado en una estación.

    Args:
        user_id (int): ID del empleado.
        marca (str): Marca de tiempo.

    Returns:
        None
    """
    query = "UPDATE registers SET exit_hour = '{}' WHERE id_employee = {} AND exit_hour IS NULL".format(marca, user_id)
    insertar_bd(query)

def get_last_register_type(user_id):
    query = "SELECT exit_hour FROM registers WHERE id_employee = {} ORDER BY id_register DESC LIMIT 1".format(user_id)
    result = execute_query(query)
    print('El resultado es ', result)
    if result and result[0][0] == None:
        return 'Exit'
    else:
        return 'Entry'
    
def get_values_for_exit(user_id):
    """
    Obtiene la línea y estación de salida más reciente de un empleado.

    Args:
    - user_id (int): ID del empleado.

    Returns:
    - tuple: Línea y estación de salida.
    """
    query = """
    SELECT production_line, production_station FROM registers WHERE id_employee = {} ORDER BY entry_hour DESC LIMIT 1
    """.format(user_id)
    results = execute_query(query)
    return results[0] if results else None

def obtener_empleados_en_la_estacion():
    """
    Obtiene los empleados que se encuentran en una estación sin haber registrado su salida.

    Returns:
    list: Resultados de la consulta.
    """
    query = """
    SELECT user_id
    FROM register
    WHERE tipo = 'Entrada' AND linea = 16 AND user_id NOT IN (
        SELECT user_id 
        FROM register 
        WHERE tipo = 'Salida' 
    )
    GROUP BY user_id
    """
    return execute_query(query)

def obtener_usuario(user_id):
    """
    Obtiene el nombre completo de un usuario a partir de su ID.

    Args:
    user_id (int): ID del usuario.

    Returns:
    str: Nombre completo del usuario.
    """
    query = "SELECT nombre_empleado, apellidos_empleado FROM table_empleados_tarjeta WHERE numero_tarjeta = {}".format(user_id)
    results = execute_query(query)

    # Devolver el primer resultado si existen resultados, de lo contrario devolver None
    # Concatena el nombre y los apellidos
    return results[0][0] + " " + results[0][1] if results else None

def obtener_imagen(user_id):
    """
    Obtiene la imagen de un usuario a partir de su ID.

    Args:
    - user_id (int): ID del usuario.

    Returns:
    - str: ID de la imagen.
    """
    query = "SELECT id_empleado FROM table_empleados_tarjeta WHERE numero_tarjeta = {}".format(user_id)
    results = execute_query(query)

    # Devolver el primer resultado si existen resultados, de lo contrario devolver None
    return results[0][0] if results else None

def get_line_id(linea):
    """
    Obtiene el ID de una línea a partir de su nombre.

    Args:
    - linea (str): Nombre de la línea.

    Returns:
    - int: ID de la línea.
    """
    query = "SELECT line_id FROM lines WHERE name = '{}'".format(linea)
    results = execute_query(query)
    return results[0][0] if results else None

def get_employees_necesary_for_line(line):
    """
    Obtiene el número total de empleados necesarios por estación de una línea.

    Args:
    - line (str): Line.

    Returns:
    - list: Resultados de la consulta.
    """
    query = """
    SELECT employee_capacity FROM lines
    WHERE name = '{}'
    """.format(line)
    return execute_query(query)

def get_names_operators(estacion, linea, posicion):
    """
    Obtiene el nombre de los operadores de una estación.

    Args:
    - estacion (str): Estación.
    - linea (str): Línea.
    - posicion (str): Posición.

    Returns:
    - list: Resultados de la consulta.
    """

    estacion_final = str(estacion) + ' ' + posicion
    
    query = """
    SELECT id_employee FROM registers
    WHERE production_station = '{}' AND production_line = '{}' AND exit_hour IS NULL
    """.format(estacion_final, linea)

    names = []
    for row in execute_query(query):
        query = """
        SELECT nombre_empleado, apellidos_empleado FROM table_empleados_tarjeta
        WHERE numero_tarjeta = '{}'
        """.format(row[0])

        names += execute_query(query)

    print(names)

    return names
