def check_name_id_exists(game_tree, name_id):
    for name in game_tree.names.values():
        if name_id == name.id:
            return True
    return False

def sort_by_days(array):
    return sorted(array, key = lambda item: item.days[0])
