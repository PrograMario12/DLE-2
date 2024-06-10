import psycopg2

def execute_query(query):
    # Establecer la conexión con la base de datos
    conn = psycopg2.connect(
        host="localhost",
        database="directlaborefficency",
        user="postgres",
        password="admin"
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

def obtener_lineas():
    query = "SELECT * FROM lines"
    return execute_query(query)

def obtener_empleados_por_linea():
    query = """
    SELECT linea, COUNT(DISTINCT user_id) 
    FROM register 
    WHERE tipo = 'Entrada' AND user_id NOT IN (
        SELECT user_id 
        FROM register 
        WHERE tipo = 'Salida' 
    )
    GROUP BY linea
    """
    return execute_query(query)