from copy import deepcopy


def drop(data, drop_list : list):

    for drop_item in drop_list:
        if isinstance(drop_item, dict):
            key = list(drop_item.keys())[0]
            data[key] = drop(data[key], drop_list=list(drop_item.values())[0])
        elif isinstance(drop_item, str):
            data.pop(drop_item, None)
        
    return data


def equivalence(data, equivalence_list : list):

    for equivalence_item in equivalence_list:

        if isinstance(equivalence_item, tuple):
            if data[equivalence_item[0]] and data[equivalence_item[0]][equivalence_item[1]]:
                data[equivalence_item[0]] = data[equivalence_item[0]][equivalence_item[1]]
        else:
            raise Exception("input format for equivalence_list is wrong")

    return data



def climb(data, climb_list : dict):

    for climb_key, climb_value in climb_list.items():
        for item in climb_value:
            data[item] = data[climb_key][item] 
        data.pop(data[climb_key], None)

    return data


def purging(
    input_data,
    drop_list : list = None,
    equivalence_list : list = None,
    climb_list : dict = None,
    ):
    data = deepcopy(input_data)

    if isinstance(data, list):
        exp_data = []
        for item in data:
            temp_data = item
            if drop_list is not None:
                temp_data = drop(data=temp_data, drop_list=drop_list)
            if climb_list is not None:
                temp_data = climb(data=temp_data, climb_list=climb_list)
            if equivalence_list is not None:
                temp_data = equivalence(data=temp_data, equivalence_list=equivalence_list)
            
            exp_data.append(temp_data)
        
        return exp_data

    if isinstance(data, dict):
        if drop_list is not None:
            data = drop(data=data, drop_list=drop_list)
        if equivalence_list is not None:
            data = equivalence(data=data, equivalence_list=equivalence_list)
        if climb_list is not None:
            data = climb(data=data, climb_list=climb_list)

        return data