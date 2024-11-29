
# Some cultures are added via decorators
registered_roommates_cultures = {
}


def register_roommates_culture(feature_id: str):

    def decorator(func):
        registered_roommates_cultures[feature_id] = func
        return func

    return decorator
