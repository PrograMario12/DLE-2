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
