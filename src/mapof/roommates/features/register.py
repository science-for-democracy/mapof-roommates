# Some features are added via decorators
registered_roommates_features = {
}

def register_roommates_feature(feature_id: str):

    def decorator(func):
        registered_roommates_features[feature_id] = func
        return func

    return decorator
