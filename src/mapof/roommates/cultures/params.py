

def get_params_for_paths(path, size, j, extremes=False):

    variable = path['variable']

    if 'extremes' in path:
        extremes = path['extremes']

    params = {'variable': variable}
    if extremes:
        params[variable] = j / (size - 1)
    elif not extremes:
        params[variable] = (j + 1) / (size + 1)

    if 'scale' in path:
        params[variable] *= path['scale']

    if 'start' in path:
        params[variable] += path['start']
    else:
        path['start'] = 0.

    if 'step' in path:
        params[variable] = path['start'] + j * path['step']

    return params, variable
