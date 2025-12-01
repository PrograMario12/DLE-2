class ActiveStaff:
    def __init__(self, id: int, name: str, last_name: str, is_active: bool):
        self.id = id
        self.name = name
        self.last_name = last_name
        self.is_active = is_active

    def __repr__(self):
        return (
            f"ActiveStaff(id={self.id}, name='{self.name}', "
            f"last_name='{self.last_name}', is_active={self.is_active})"
        )
