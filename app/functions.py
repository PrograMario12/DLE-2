import psycopg2
from config import Config

class Usuario:
    def __init__(self, numero_empleado, hora, linea):
        self.numero_empleado = numero_empleado
        self.hora = hora
        self.linea = linea

    def set_numero_empleado(self, numero_empleado):
        self.numero_empleado = numero_empleado

    def set_hora(self, hora):
        self.hora = hora
    
    def set_linea(self, linea):
        self.linea = linea

    def __str__(self):
        return "Número de empleado: {}, Hora: {}, Línea: {}".format(self.numero_empleado, self.hora, self.linea)

def execute_query(query):
    # Establecer la conexión con la base de datos
    conn = psycopg2.connect(
        host=Config.DATABASE_HOST,
        database= Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
    )

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
    # Establecer la conexión con la base de datos
    conn = psycopg2.connect(
        host=Config.DATABASE_HOST,
        database= Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PASSWORD
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
    query = "SELECT * FROM lines"
    return execute_query(query)

def obtener_empleados_por_linea():
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
    query = "SELECT * FROM stations WHERE line_id = {} ORDER BY station_number, posicion".format(linea)
    return execute_query(query)

def obtener_empleados_por_estacion(linea):
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
    query = "INSERT INTO register (user_id, linea, estacion, tipo, marca) VALUES ({}, '{}', '{}', '{}', '{}')".format(user_id, linea, estacion, tipo, marca)
    insertar_bd(query)

def obtener_tipo_registro(user_id):
    query = "SELECT tipo FROM register WHERE user_id = {} ORDER BY marca DESC LIMIT 1".format(user_id)
    results = execute_query(query)
    results = results[0][0] if results else None
    if results == "Entrada":
        return "Salida"
    else:
        return "Entrada"
    
def obtener_valores_salida(user_id):
    query = "SELECT linea, estacion FROM register WHERE user_id = {} ORDER BY marca DESC LIMIT 1".format(user_id)
    results = execute_query(query)
    return results[0] if results else None

def obtener_empleados_en_la_estacion():
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
    query = "SELECT nombre_empleado, apellidos_empleado FROM table_empleados_tarjeta WHERE numero_tarjeta = {}".format(user_id)
    results = execute_query(query)
    print(results)

    # Devolver el primer resultado si existen resultados, de lo contrario devolver None
    #Concatena el nombre y los apellidos
    return results[0][0] + " " + results[0][1] if results else None

def obtener_imagen(user_id):
    query = "SELECT id_empleado FROM table_empleados_tarjeta WHERE numero_tarjeta = {}".format(user_id)
    results = execute_query(query)

    # Devolver el primer resultado si existen resultados, de lo contrario devolver None
    return results[0][0] if results else None