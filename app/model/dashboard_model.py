''' Model for the dashboard '''
from app.database import Database

class LinesDashboard():
    ''' Class to represent the lines in the dashboard '''
    def __init__(self):
        self.db = Database()

    def create_lines_dashboard(self):
        ''' Create a dictionary with the lines '''
        lines = self.get_line()
        lines_data = self.create_cards(lines)
        self.add_employees_data(lines_data)
        self.add_classes(lines_data)
        active_lines = self.get_active_lines(lines_data)
        self.add_status(lines_data, active_lines)
        return lines_data  # lines_data contains the processed line
        # cards with employee data, classes, and status

    def create_cards(self, lines):
        ''' Create cards from lines '''
        lines_data = []
        for line in lines:
            card = {
                'name': f"{line[3]} {line[1]}",
                'id': line[0],
                'employee_capacity': line[2],
            }
            lines_data.append(card)
        return lines_data

    def add_employees_data(self, lines_data):
        ''' Add employees data to cards '''
        employees = self.get_employees_actives()
        employees = [(int(emp[0]), emp[1]) for emp in employees]
        for employee_id, employees_working in employees:
            for card in lines_data:
                card_id = int(card['id'])
                if card_id == employee_id:
                    card['employees_working'] = employees_working
                    percentage = (
                        employees_working / card['employee_capacity']
                        ) * 100
                    card['percentage'] = round(percentage, 2)

    def add_classes(self, lines_data):
        ''' Add classes to cards based on percentage '''
        class_mapping = {
            'employee-warning': lambda p: p > 100,
            'employee-nook': lambda p: p < 100,
            'employee-ok': lambda p: p == 100
        }
        for card in lines_data:
            if 'percentage' in card:
                for class_name, condition in class_mapping.items():
                    if condition(card['percentage']):
                        card['class'] = class_name
                        break

    def get_active_lines(self, lines_data):
        ''' Get active lines from cards '''
        active_lines = []
        for card in lines_data:
            if 'employees_working' in card:
                active_lines.append(card['id'])
        return active_lines

    def add_status(self, lines_data, active_lines):
        ''' Add status to cards based on active lines '''
        status = self.get_status_lines(active_lines)
        for card in lines_data:
            if card['id'] in status and card['percentage'] == 100:
                card['status'] = False
            else:
                card['status'] = True

    def get_line(self):
        ''' Get the name of the line '''
        self.db.connect()
        query = """
            SELECT *
            FROM zones ORDER BY name
        """
        lines = self.db.execute_query(query)
        self.db.disconnect()

        return lines

    def get_employees_actives(self):
        ''' Get the employees actives '''
        self.db.connect()
        query = """
            SELECT line_id_fk, count(id_employee) AS employees_working
            FROM registers
            WHERE entry_hour IS NOT NULL and exit_hour is NULL
            GROUP BY line_id_fk
        """
        employees = self.db.execute_query(query)
        self.db.disconnect()

        return employees

    def get_status_lines(self, active_lines):
        ''' Get the status of the lines '''
        self.db.connect()

        active_lines_str = ','.join(map(str, active_lines))

        query_employees_actives_for_station = f"""
            SELECT
              r.line_id_fk,
              r.position_id_fk,
              COUNT(*) AS employees_working
            FROM registers r
			INNER JOIN tbl_sides_of_positions tbl_p 
              ON r.position_id_fk = tbl_p.side_id
			INNER JOIN positions ps 
              ON tbl_p.position_id_fk = ps.position_id
            WHERE r.entry_hour IS NOT NULL
                AND r.exit_hour IS NULL
                AND r.line_id_fk IN ({active_lines_str})
            GROUP BY r.line_id_fk, r.position_id_fk;
        """
        print(query_employees_actives_for_station)

        query_employees_necessary_for_station = f"""
            SELECT
              p.line_id,
              tbl_p.side_id,
              tbl_p.employee_capacity 
            FROM positions p
            INNER JOIN tbl_sides_of_positions tbl_p
              ON tbl_p.position_id_fk = p.position_id
            WHERE p.line_id in ({active_lines_str})
            AND p.position_name NOT LIKE '%afe%'
        """

        employees_actives = self.db.execute_query(
                query_employees_actives_for_station
            )
        employees_necessary = self.db.execute_query(
                query_employees_necessary_for_station
            )

        self.db.disconnect()

        necessary_dict = {}

        if employees_actives:
            active_dict = {(line_id, pos_id): count for line_id, pos_id, count
                        in employees_actives
                        }
            necessary_dict = {(line_id, pos_id): count for line_id, pos_id, count
                            in employees_necessary
                            }

        lines_not_complete = {
            line_id for (line_id, pos_id), count in necessary_dict.items()
            if active_dict.get((line_id, pos_id), 0) < count
        }

        return list(lines_not_complete)

class StationsDashboard():
    ''' Class to represent the stations in the dashboard '''
    def __init__(self):
        self.db = Database()

    def create_stations_dashboard(self, line):
        ''' Create a dictionary with the stations '''
        stations = self.get_stations(line)
        employees_active = {emp[0]: emp[1]
                            for emp in self.get_employees_actives(line)}

        positions = {}
        for station in stations:
            position_id = station[0]
            if position_id not in positions:
                positions[position_id] = {
                    'name': station[1],
                    'status': station[2],
                    'sides': []
                }
            positions[position_id]['sides'].append({
                'side_id': station[3],
                'side_title': station[4],
                'employee_capacity': station[5],
                'employees_working': employees_active.get(station[3], 0)
            })

        card_data = []
        for position_id, position_data in positions.items():
            card = {
                'position_id': position_id,
                'position_name': position_data['name'],
                'status': position_data['status'],
                'sides': position_data['sides']
            }
            for side in card['sides']:
                if side['employee_capacity'] > side['employees_working']:
                    side['class'] = 'employee-warning'
                elif side['employee_capacity'] == side['employees_working']:
                    side['class'] = 'employee-ok'
                else:
                    side['class'] = 'employee-nook'
            card_data.append(card)

        return card_data

    def get_employees_actives(self, line):
        ''' Get the employees actives '''
        self.db.connect()
        query = f"""
            SELECT position_id_fk, COUNT(*) AS employees_working
            FROM registers
            WHERE entry_hour IS NOT NULL and exit_hour is NULL
            AND line_id_fk = {line}
            GROUP BY position_id_fk
        """
        employees = self.db.execute_query(query)
        self.db.disconnect()

        return employees

    def get_line(self, line):
        ''' Get the name of the line '''
        self.db.connect()
        query = f"""
            SELECT type_zone || ' ' || name AS line
            FROM zones WHERE line_id = {line}
        """
        line = self.db.execute_query(query)
        self.db.disconnect()

        line = str(line[0][0]) if line else "registra una línea"

        return line

    def get_stations(self, line):
        ''' Get the stations '''
        self.db.connect()
        query = f"""
            SELECT
              pos.position_id,
              pos.position_name,
              ps.is_active,
              sides.side_id,
              sides.side_title,
              sides.employee_capacity
            FROM positions pos
			INNER JOIN tbl_sides_of_positions sides
              ON sides.position_id_fk = pos.position_id
            INNER JOIN position_status ps 
              ON ps.position_id_fk = pos.position_id

            WHERE line_id = {line}
            ORDER BY position_name, sides.side_title
        """
        stations = self.db.execute_query(query)
        self.db.disconnect()
        return stations

class OperatorsDashboard():
    ''' Class to represent the operators in the dashboard '''
    def __init__(self):
        self.db = Database()

    def get_operators(self, station):
        ''' Get the operators '''
        self.db.connect()
        query_active_employees = f"""
            SELECT
              id_employee,
              entry_hour
            FROM registers
            WHERE entry_hour IS NOT NULL and exit_hour is NULL
            AND position_id_fk = {station}
        """
        operators = self.db.execute_query(query_active_employees)
        operators_id = [operator[0] for operator in operators]

        query_data_employees = f"""
            SELECT
              numero_tarjeta,
              id_empleado,
              nombre_empleado,
              apellidos_empleado
            FROM table_empleados_tarjeta
            WHERE numero_tarjeta IN ({','.join(map(str, operators_id))})
        """
        operators_data = self.db.execute_query(query_data_employees)
        self.db.disconnect()


        active_operators = []
        for operator in operators:
            operator_id = operator[0]
            operator_info = next((
                data for data in operators_data
                if data[0] == operator_id
                ), None)
            if operator_info:
                active_operators.append(str(operator_info[1])
                                        + ' '
                                        + operator_info[2]
                                        + ' '
                                        + operator_info[3]
                                    )
            else:
                active_operators.append("Operador aún no registrado")

        return active_operators
