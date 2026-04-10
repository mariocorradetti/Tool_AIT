class Router:
    def __init__(self, parent):
        self.parent = parent
        self.routes = {}       # {"tool_name": UI_class}
        self.current_widget = None

    def register(self, name, widget_class):
        self.routes[name] = widget_class

    def navigate(self, name):
        if self.current_widget:
            self.current_widget.pack_forget()
        widget_cls = self.routes.get(name)
        if widget_cls:
            self.current_widget = widget_cls(self.parent)
            self.current_widget.pack(fill="both", expand=True)