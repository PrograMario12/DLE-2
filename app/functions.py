import psycopg2
from config import Config

'''
Funciones para interactuar con la base de datos.
- execute_query(query): Ejecuta una consulta en la base de datos.
- insertar_bd(query): Inserta datos en la base de datos.
- obtener_lineas(): Obtiene todas las líneas.
- obtener_empleados_por_linea(): Obtiene el número total de empleados por línea.
- obtener_estaciones(linea): Obtiene todas las estaciones de una línea.
- obtener_empleados_por_estacion(linea): Obtiene el número total de empleados por estación de una línea.
- registar_entrada_salida(user_id, linea, estacion, tipo, marca): Registra la entrada o salida de un empleado en una estación.
- obtener_tipo_registro(user_id): Obtiene el tipo de registro (Entrada o Salida) más reciente de un empleado.
- obtener_valores_salida(user_id): Obtiene la línea y estación de salida más reciente de un empleado.
- obtener_empleados_en_la_estacion(): Obtiene los empleados que se encuentran en una estación sin haber registrado su salida.
- obtener_usuario(user_id): Obtiene el nombre completo de un usuario a partir de su ID.
- obtener_imagen(user_id): Obtiene la imagen de un usuario a partir de su ID.
- get_line_id(linea): Obtiene el ID de una línea a partir de su nombre.
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
    print('Entré a la función')
    print(query)
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

def obtener_lineas():
    """
    Obtiene todas las líneas.

    Returns:
    - list: Resultados de la consulta.
    """
    query = """
            SELECT * 
            FROM lines 
            ORDER BY CAST(SUBSTRING(name, 1, 2) AS INTEGER) DESC;
            """
    return execute_query(query)

def obtener_empleados_por_linea():
    """
    Obtiene el número total de empleados por línea.

    Returns:
    - list: Resultados de la consulta.
    """
    query = """
    SELECT linea, COUNT(user_id) AS total_users
        FROM register
        WHERE (tipo = 'Entrada' AND (id_register, user_id) IN (
            SELECT MAX(id_register), user_id
            FROM register
            GROUP BY user_id
        ))
        GROUP BY linea;
    """
    return execute_query(query)

def obtener_estaciones(linea):
    """
    Obtiene todas las estaciones de una línea.

    Args:
    - linea (str): Línea.

    Returns:
    - list: Resultados de la consulta.
    """
    query = "SELECT * FROM stations WHERE line_id = {} ORDER BY station_number, posicion".format(linea)
    return execute_query(query)

def obtener_empleados_por_estacion(linea):
    """
    Obtiene el número total de empleados por estación de una línea.

    Args:
    - linea (str): Línea.

    Returns:
    - list: Resultados de la consulta.
    """
    query = """
    SELECT estacion, COUNT(user_id) AS total_users
        FROM register
        WHERE (tipo = 'Entrada' AND (id_register, user_id) IN (
            SELECT MAX(id_register), user_id
            FROM register
            GROUP BY user_id
        ))
        AND linea = '{}'
        GROUP BY estacion;
    """.format(linea)
    return execute_query(query)

def registar_entrada_salida(user_id, linea, estacion, tipo, marca):
    """
    Registra la entrada o salida de un empleado en una estación.

    Args:
    - user_id (int): ID del empleado.
    - linea (str): Línea.
    - estacion (str): Estación.
    - tipo (str): Tipo de registro (Entrada o Salida).
    - marca (str): Marca de tiempo.
    """
    query = "INSERT INTO register (user_id, linea, estacion, tipo, marca) VALUES ({}, '{}', '{}', '{}', '{}')".format(user_id, linea, estacion, tipo, marca)
    insertar_bd(query)

def obtener_tipo_registro(user_id):
    """
    Obtiene el tipo de registro (Entrada o Salida) más reciente de un empleado.

    Args:
    - user_id (int): ID del empleado.

    Returns:
    - str: Tipo de registro.
    """
    query = "SELECT tipo FROM register WHERE user_id = {} ORDER BY marca DESC LIMIT 1".format(user_id)
    results = execute_query(query)
    results = results[0][0] if results else None
    if results == "Entrada":
        return "Salida"
    else:
        return "Entrada"
    
def obtener_valores_salida(user_id):
    """
    Obtiene la línea y estación de salida más reciente de un empleado.

    Args:
    - user_id (int): ID del empleado.

    Returns:
    - tuple: Línea y estación de salida.
    """
    query = "SELECT linea, estacion FROM register WHERE user_id = {} ORDER BY marca DESC LIMIT 1".format(user_id)
    results = execute_query(query)
    return results[0] if results else None

def obtener_empleados_en_la_estacion():
    """
    Obtiene los empleados que se encuentran en una estación sin haber registrado su salida.

    Returns:
    - list: Resultados de la consulta.
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
    - user_id (int): ID del usuario.

    Returns:
    - str: Nombre completo del usuario.
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