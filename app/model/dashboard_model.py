''' Model for the dashboard '''
from app.database import Database

class LinesDashboard():
    ''' Class to represent the lines in the dashboard '''
    def __init__(self):
        self.db = Database()

    def create_dictionary(self):
        ''' Create a dictionary with the lines '''

        lines = self.get_line()

        cars_data = []
        for line in lines:
            card = {
                'name': f"{line[3]} {line[1]}",
                'id': line[0],
                'employee_capacity': line[2],
            }
            cars_data.append(card)

        employees = self.get_employees_actives()
        for employee in employees:
            for card in cars_data:
                if int(card['id']) == int(employee[0]):
                    card['employees_working'] = employee[1]
                    card['percentage'] = round(
                        (card['employees_working']
                        / card['employee_capacity']) * 100, 2)

        for card in cars_data:
            if 'percentage' in card:
                if card['percentage'] > 100:
                    card['class'] = 'employee-warning'
                elif card['percentage'] < 100:
                    card['class'] = 'employee-nook'
                else:
                    card['class'] = 'employee-ok'

        active_lines = []
        for card in cars_data:
            if 'employees_working' in card:
                active_lines.append(card['id'])

        status = self.get_status_lines(active_lines)
        for card in cars_data:
            if card['id'] in status and card['percentage'] == 100:
                card['status'] = False
            else:
                card['status'] = True

        print(cars_data)

        return cars_data

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
        query_employees_actives_for_station = f"""
            SELECT line_id_fk,
                position_id_fk,
                COUNT(*) AS employees_working
            FROM registers
            WHERE entry_hour IS NOT NULL
                AND exit_hour IS NULL
                AND line_id_fk
                IN ({','.join([str(line) for line in active_lines])})
            GROUP BY line_id_fk, position_id_fk;
        """

        query_employees_necessary_for_station = F"""
            SELECT line_id, position_id, COUNT(*) AS employees_necessary
            FROM positions
            WHERE line_id
            IN ({','.join([str(line) for line in active_lines])})
            AND position_name NOT LIKE '%nva%'
            AND position_name NOT LIKE '%afe%'
            GROUP BY line_id, position_id;
        """

        employees_actives = self.db.execute_query(
                query_employees_actives_for_station
            )

        employees_necessary = self.db.execute_query(
                query_employees_necessary_for_station
            )
        self.db.disconnect()

        different = []
        for register in employees_necessary:
            if register not in employees_actives:
                different.append(register)

        lines_not_complete = []
        for diff in different:
            if diff[0] not in lines_not_complete:
                lines_not_complete.append(diff[0])

        return lines_not_complete
