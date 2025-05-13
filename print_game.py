def print_routes(names, route, parent_deaths = {}, depth = 0):
    multiplier = 2
    print((" " * (depth * multiplier)) + f"Title: {route.name}")
    
    deaths = parent_deaths.copy()
    if len(route.deaths) > 0:
        print((" " * ((depth) * multiplier)) + f"Deaths:", end = " ")
        for death_key in route.deaths:
            death = route.deaths[death_key]
            if death_key in deaths:
                parent_death = deaths[death_key]
                death.count += parent_death.count
                death.days = parent_death.days + death.days
            deaths[death_key] = death
    if len(deaths) > 0:
        for death in deaths.values():
            print(names[death.id].full, "died", death.count, "time(s)", "on day(s)", str(death.days)[1 : -1], end = "; ")
        print("")
    
    if route.branch:
        choices = route.branch.choices
        for i in range(len(choices)):
            choice = choices[i]
            print((" " * ((depth) * multiplier)) + f"Decide: {choice.name} on {route.branch.name:}")
            print_routes(names, choice.route, deaths, depth + 1)

def print_tree(game_tree):
        for route_key in game_tree.base_routes:
            print_routes(game_tree.names, game_tree.base_routes[route_key])
            print("")