# Some distances are added via decorators
registered_roommates_distances = {
}

def register_roommates_distance(feature_id: str):

    def decorator(func):
        registered_roommates_distances[feature_id] = func
        return func

    return decorator
