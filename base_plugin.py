class Plugin:
    name = "Unspecified Plugin"
    requirements = []

    #dictionary of: event type -> list of callback functions
    subscribers = {}

    def __init__(self, mediator, *args, **kwargs):
        pass

    """
    We've got a subcriber/observer design pattern here. Here's how it works:
    (1) Each plugin maintains a list of requirements it needs, that is, other classes.
    (2) It also should take each of those as args to its __init__
    (3) At runtime, the Mediator class instantiates one of each plugin
    (4) and then passes plugins the references to their requirements
        (assumption: no circular requirements allowed)
    (5) A plugin in its __init__ can then call the attach method
        of each of its requirements, handing them callback functions.
    (6) The subscribables implement ahead of time what to do with the callbacks. 
    """
    def attach_subscriber(self, event_type, callback):
        if event_type in self.subscribers:
            self.subscribers[event_type] += callback,
        else:
            self.subscribers[event_type] = [callback]
        print(f"Attaching callback to {self.name} for '{event_type}'.")

    def notify(self, event_type, *args, **kwargs):
        for callback in self.subscribers[event_type]:
            callback(*args, **kwargs)
