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
        lines_data = self.create_cards(lines)
        self.add_employees_data(lines_data)
        self.add_classes(lines_data)
        active_lines = self.get_active_lines(lines_data)
        self.add_status(lines_data, active_lines)
        print(lines_data)
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
                    percentage = (employees_working / card['employee_capacity']) * 100
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
