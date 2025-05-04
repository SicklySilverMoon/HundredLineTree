import json
import sys
import os
from string import whitespace

class Name:
    def __init__(self, id = None, full = None, first = None, last = None, title = None, position = None):
        self.id = id
        self.full = full
        self.first = first
        self.last = last
        self.title = title
        self.position = position

class Death:
    def __init__(self, id, count, days):
        self.id = id
        self.count = count
        self.days = days
    
    def __str__(self):
        return f"Death{{id: {self.id}, count: {self.count}, days: {self.days}}}"

    def __repr__(self):
        return self.__str__()

class Event:
    def __init__(self, name, days):
        self.name = name
        self.days = days

class Choice:
    def __init__(self, branch, direction, name):
        self.branch = branch
        self.direction = direction
        self.name = name
        self.route = None
    
    def set_route(self, route):
        self.route = route

class Branch:
    def __init__(self, parent, name, day):
        self.parent = parent
        self.name = name
        self.day = day
        self.choices = {"left": None, "right": None}
        
        self.parent.branch = self
        
    def set_choice(self, choice):
        self.choices[choice.direction] = choice

class Route:
    def __init__(self, parent, name, deaths = {}):
        self.parent = parent
        self.name = name
        
        if parent:
            for parent_death_key in parent.deaths:
                parent_death = parent.deaths[parent_death_key]
                if parent_death.id not in deaths:
                    deaths[parent_death.id] = parent_death
                else:
                    child_death = deaths[parent_death.id]
                    child_death.count += parent_death.count
                    child_death.days = sorted(parent_death.days + child_death.days)
                    deaths[child_death.id] = child_death
        self.deaths = deaths
        
        self.events = []
        self.branch = None
    
    def set_branch(self, branch):
        self.branch = branch

class Tree:
    def __init__(self, names):
        self.names = names
        self.base_routes = {}
    
    def add_route(self, route):
        self.base_routes[route.name] = route

def whitespace_start(string):
    return string.startswith(tuple(w for w in whitespace))

def parse_route(parent_route, route_json, depth = 0):
    #print(route_json)
    deaths = {}
    if "deaths" in route_json:
        for death_json in route_json["deaths"]:
            deaths[death_json["id"]] = (Death(death_json["id"], death_json["count"], death_json["days"]))
    #print(deaths)
    #print("")
    
    route = Route(parent_route, route_json["name"], deaths)
    
    events = []
    if "events" in route_json:
        for event_json in route_json["events"]:
            events.append(Event(event_json["name"], event_json["days"]))
        route.events = events
        #todo: sort on event.days[0] as the key
    
    #if depth == 0:
    #    print(route.name)
    if "branch" in route_json:
        branch_json = route_json["branch"]
        branch = Branch(route, branch_json["name"], branch_json["day"])
        for choice_json in branch_json["choices"]:
            choice = Choice(branch, choice_json["direction"], choice_json["name"])
            route_ret = parse_route(route, choice_json["route"], depth + 1)
            choice.set_route(route_ret)
            branch.set_choice(choice)
    
    #if depth == 0:
    #    print(route.name)
    return route

def parse_game_data(data_json):
    names = {}
    for name_json in data_json["names"]:
        names[name_json["id"]] = Name(**name_json)
    game_tree = Tree(names)
    
    for route_json in data_json["routes"]:
        base_route = parse_route(None, route_json)
        game_tree.base_routes[base_route.name] = base_route
    
    return game_tree

def print_routes(names, route, depth = 0):
    multiplier = 2
    print((" " * (depth * multiplier)) + f"Title: {route.name}")
    
    if len(route.deaths) > 0:
        print((" " * ((depth) * multiplier)) + f"Deaths:", end = " ")
        for death_key in route.deaths:
            death = route.deaths[death_key]
            print(names[death.id].full, "died", death.count, "time(s)", "on day(s)", str(death.days)[1 : -1], end = "; ")
        print("")
    
    if route.branch:
        print((" " * ((depth) * multiplier)) + f"Decide: {route.branch.choices["left"].name} on {route.branch.name:}")
        print_routes(names, route.branch.choices["left"].route, depth + 1)
        print((" " * ((depth) * multiplier)) + f"Decide: {route.branch.choices["right"].name} on {route.branch.name:}")
        print_routes(names, route.branch.choices["right"].route, depth + 1)

def edit_recurse(game_tree, route):
    pass

def edit(game_tree):
    pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} json_file")
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        data = json.load(f)
    
    game_tree = parse_game_data(data)
    
    response = input("1 to display file, 2 to edit: ")
    
    if int(response) == 1:
        for route_key in game_tree.base_routes:
            print_routes(game_tree.names, game_tree.base_routes[route_key])
            print("")
    elif int(response) == 2:
        edit(game_tree)
        pass
