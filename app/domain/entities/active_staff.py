class ActiveStaff:
    def __init__(self, id: int, name: str, last_name: str, is_active: bool, entry_time: str = None, line_name: str = None):
        self.id = id
        self.name = name
        self.last_name = last_name
        self.is_active = is_active
        self.entry_time = entry_time
        self.line_name = line_name

    def __repr__(self):
        return (
            f"ActiveStaff(id={self.id}, name='{self.name}', "
            f"last_name='{self.last_name}', is_active={self.is_active}, "
            f"entry_time='{self.entry_time}', line_name='{self.line_name}')"
        )
