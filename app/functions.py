''' Module for queries to the database. '''

from datetime import datetime

import psycopg2
from config import Config


class User:
    ''' This class represents a user. '''
    def __init__(self, employee_number, hour, line):
        self.employee_number = employee_number
        self.hour = hour
        self.line = line

    def set_employee_number(self, employee_number):
        ''' Set the employee number. '''
        self.employee_number = employee_number

    def set_hour(self, hour):
        ''' Set the hour. '''
        self.hour = hour

    def set_line(self, line):
        """
        Establece la línea.

        Args:
        - line (str): Línea.
        """
        self.line = line

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Usuario.

        Returns:
        - str: Representación en cadena del objeto Usuario.
        """
        return f"""Número de empleado: {self.employee_number},
                Hora: {self.hour}, Línea: {self.line}"""

def execute_query(query):
    """
    Executes a query in the database.

    Args:
    - query (str): SQL query.

    Returns:
    - list: Query results.
    """
    # Establish a connection to the database
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

    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results

def insert_bd(query):
    """
    Insert data into the database.

    Args:
    - query (str): SQL query.
    """
    # Establish a connection to the database
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
    ''' Gets the zones. '''
    query = """
        SELECT line_id, type_zone || ' ' || name, employee_capacity
        FROM zones
        ORDER BY CASE
            WHEN name ~ '[0-9]' THEN CAST(SUBSTRING(name, '^[0-9]+') 
            AS INTEGER)
            ELSE 0
        END DESC;
        """
    return execute_query(query)

def get_stations(line):
    ''' Gets the stations. '''
    if line == 6:
        query = f"""
        SELECT position_name,
            MAX(CASE WHEN side IN ('LH', 'BP')
            THEN employee_capacity END)
                AS employee_capacity_lh_or_bp,
            COALESCE(MAX(CASE WHEN side = 'RH'
            THEN employee_capacity END), 0) AS employee_capacity_rh
        FROM positions
        WHERE line_id = {line}
        AND position_id IN (
            SELECT position_id_fk
            FROM position_status
            WHERE is_active = True
        )
        GROUP BY position_name
        ORDER BY position_name;
        """
    else:
        query = f"""
            SELECT position_name,
                MAX(CASE WHEN side IN ('LH', 'BP')
                    THEN employee_capacity END)
                        AS employee_capacity_lh_or_bp,
                COALESCE(MAX(CASE WHEN side = 'RH'
                    THEN employee_capacity END), 0) 
                        AS employee_capacity_rh
            FROM positions
            WHERE line_id = {line}
            GROUP BY position_name
            ORDER BY position_name;
            """
    return execute_query(query)

def get_employees_for_line(linea=None):
    ''' Gets the employees for a line. '''
    if linea:
        query = f"""
        SELECT production_line, count(id_employee) AS employees_working
            FROM registers
            WHERE entry_hour IS NOT NULL and exit_hour is NULL 
            AND production_line = '{linea}'
            GROUP BY production_line
        """
    else:
        query = """
        SELECT production_line, count(id_employee) AS employees_working
            FROM registers
            WHERE entry_hour IS NOT NULL and exit_hour is NULL
            GROUP BY production_line
        """
    return execute_query(query)

def get_employees_for_station(line):
    """ Gets the employees for a station. """

    line = ' '.join(line.split()[1:])

    query = f"""
    SELECT production_station, COUNT(*) AS employees_working
        FROM registers
        WHERE entry_hour IS NOT NULL AND exit_hour IS NULL
        AND production_line = '{line}'
        GROUP BY production_station;
    """

    return execute_query(query)

def register_entry(user_id, line, station, mark):
    """
    Registers the entry of an employee at a station.

    Args:
        user_id (int): Employee ID.
        line (str): Line.
        station (str): Station.
        mark (str): Timestamp.

    Returns:
        None
    """
    today_date = datetime.now().strftime("%Y-%m-%d")
    query = f"""
        INSERT INTO registers
            (id_employee, date_register, production_line,
             production_station, entry_hour)
        VALUES (
            {user_id}, '{today_date}', '{line}', '{station}', '{mark}'
        )
        """
    insert_bd(query)

def register_exit(user_id, mark):
    """
    Registers the exit of an employee at a station.

    Args:
        user_id (int): Employee ID.
        mark (str): Timestamp.

    Returns:
        None
    """
    query = f"""
    UPDATE registers
        SET exit_hour = '{mark}'
        WHERE id_employee = {user_id} AND exit_hour IS NULL
    """
    insert_bd(query)

def get_last_register_type(user_id):
    ''' Gets the last register type. '''
    query = f"""
    SELECT exit_hour
        FROM registers
        WHERE id_employee = {user_id}
        ORDER BY id_register DESC
        LIMIT 1
    """

    result = execute_query(query)
    if result and result[0][0] is None:
        return 'Exit'
    return 'Entry'



def get_values_for_exit(user_id):
    ''' Gets the values for exit. '''
    query = f"""
    SELECT production_line, production_station
        FROM registers
        WHERE id_employee = {user_id}
        ORDER BY id_register DESC
        LIMIT 1
    """
    results = execute_query(query)
    return results[0] if results else None


def get_user(user_id):
    '''Gets the user based on their ID. '''
    query = f"""
    SELECT nombre_empleado, apellidos_empleado 
        FROM table_empleados_tarjeta
        WHERE numero_tarjeta = {user_id}
    """
    results = execute_query(query)

    return results[0][0] + " " + results[0][1] if results else None

def get_image(user_id):
    """
    Gets the image of a user based on their ID.

    Args:
    - user_id (int): User ID.

    Returns:
    - str: Image ID.
    """
    query = f"""
    SELECT id_empleado
        FROM table_empleados_tarjeta
        WHERE numero_tarjeta = {user_id}
    """
    results = execute_query(query)

    return results[0][0] if results else None

def get_line_id(line):
    ''' Gets the line ID. '''
    query = f"""SELECT line_id
            FROM zones 
            WHERE LOWER(type_zone) || ' ' || LOWER(name) =
            '{line.lower()}'"""
    
    print (query)
    results = execute_query(query)
    return results[0][0] if results else None

def get_employees_necessary_for_line(line):
    ''' Gets the employees necessary for a line. '''

    if line == 'inyectoras':
        query = """
        SELECT count(*)
            FROM position_status ps
            INNER JOIN positions p ON p.position_id = ps.position_id_fk
            WHERE ps.is_active is TRUE
            AND line_id = 6
        """
    else:
        line = get_line_id(line)
        query = f"""
        SELECT employee_capacity
            FROM zones
            WHERE line_id = {line}
        """

    return execute_query(query)

def get_names_operators(station, line, position):
    ''' Gets the names of the operators. '''
    final_station = str(station) + ' ' + position

    query = f"""
    SELECT table_empleados_tarjeta.nombre_empleado,
     table_empleados_tarjeta.apellidos_empleado,
     table_empleados_tarjeta.id_empleado
        FROM registers
        JOIN table_empleados_tarjeta ON registers.id_employee
        = table_empleados_tarjeta.numero_tarjeta
        WHERE registers.production_station = '{final_station}'
        AND registers.production_line = '{line}'
        AND exit_hour IS NULL
    """

    names = []
    results = execute_query(query)

    for result in results:
        if result[0] and result[1] and result[2]:
            full_name = f'{result[2]} {result[0]} {result[1]}'
            names.append(full_name)
        else:
            names.append('Información de usuario aún no disponible')

    return names
