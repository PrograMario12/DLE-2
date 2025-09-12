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