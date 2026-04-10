class ProcedureLogic:
    def __init__(self, excel_manager):
        self.excel = excel_manager
        self.current_row = self.excel.find_last_signed() + 1

    def next_step(self):
        self.current_row += 1

    def previous_step(self):
        if self.current_row > 2:
            self.current_row -= 1