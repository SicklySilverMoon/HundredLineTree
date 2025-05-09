import json
from json import JSONEncoder
import sys
from utils import sort_by_days

class Name:
    def __init__(self, id = None, full = None, first = None, last = None, title = None, position = None, web_title = None):
        self.id = id.lower()
        self.full = full
        self.first = first
        self.last = last
        self.title = title
        self.position = position
        self.web_title = web_title
    
    def as_dict(self):
        d = {}
        if self.id:
            d["id"] = self.id
        if self.full:
            d["full"] = self.full
        if self.first:
            d["first"] = self.first
        if self.last:
            d["last"] = self.last
        if self.title:
            d["title"] = self.title
        if self.position:
            d["position"] = self.position
        if self.web_title:
            d["web_title"] = self.web_title
        return d

class Death:
    def __init__(self, id, count, days):
        self.id = id.lower()
        self.count = count
        self.days = days
    
    def as_dict(self):
        d = {}
        if self.id:
            d["id"] = self.id
        d["count"] = self.count if self.count else -1
        d["days"] = self.days if self.days else [-1]
        return d
    
    def __str__(self):
        return f"Death{{id: {self.id}, count: {self.count}, days: {self.days}}}"

    def __repr__(self):
        return self.__str__()

class Event:
    def __init__(self, name, days):
        self.name = name
        self.days = days
    
    def as_dict(self):
        d = {}
        d["name"] = self.name if self.name else "[UNKNOWN]"
        d["days"] = self.days if self.days else [-1]
        return d

class Choice:
    def __init__(self, branch, direction, name):
        self.branch = branch
        self.direction = direction
        self.name = name
        self.route = None
        
        self.branch.set_choice(self)
    
    def set_route(self, route):
        self.route = route
    
    def as_dict(self):
        d = {}
        d["direction"] = self.direction
        d["name"] = self.name if self.name else "[UNKNOWN]"
        if self.route:
            d["route"] = self.route.as_dict()
        return d

class Branch:
    def __init__(self, parent, name, day):
        self.parent = parent
        self.name = name
        self.day = day
        self.choices = []
        
        self.parent.branch = self
        
    def set_choice(self, choice):
        self.choices.append(choice)
    
    def as_dict(self):
        d = {}
        d["name"] = self.name if self.name else "[UNKNOWN]"
        d["day"] = self.day if self.day else -1
        choices = []
        for choice in self.choices:
            choices.append(choice.as_dict())
        d["choices"] = choices
        return d

class Route:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        
        self.deaths = {}
        
        self.events = []
        self.branch = None
    
    def set_deaths(self, deaths):
        self.deaths = deaths
    
    def set_events(self, events):
        self.events = events
    
    def set_branch(self, branch):
        self.branch = branch
    
    def as_dict(self):
        d = {}
        d["name"] = self.name if self.name else "[UNKNOWN]"
        if self.deaths:
            d["deaths"] = []
            for death in self.deaths.values():
                d["deaths"].append(death.as_dict())
        if self.events:
            d["events"] = []
            for event in self.events:
                d["events"].append(event.as_dict())
        if self.branch:
            d["branch"] = self.branch.as_dict()
        return d

class Tree:
    def __init__(self, names):
        self.names = names
        self.base_routes = {}
    
    def add_route(self, route):
        self.base_routes[route.name] = route
    
    def as_dict(self):
        d = {}
        if self.names:
            d["names"] = []
            for name in self.names.values():
                d["names"].append(name.as_dict())
        d["routes"] = []
        for route in self.base_routes.values():
            d["routes"].append(route.as_dict())
        return d

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        return obj.as_dict()

def parse_route(parent_route, route_json, depth = 0):    
    route = Route(parent_route, route_json["name"])
    
    events = []
    if "events" in route_json:
        for event_json in route_json["events"]:
            events.append(Event(event_json["name"], event_json["days"]))
        route.set_events(sort_by_days(events))
    
    deaths = []
    if "deaths" in route_json:
        for death_json in route_json["deaths"]:
            deaths.append(Death(death_json["id"], death_json["count"], death_json["days"]))
        deaths = sort_by_days(deaths)
        route.set_deaths({d.id:d for d in deaths})
    
    if "branch" in route_json:
        branch_json = route_json["branch"]
        branch = Branch(route, branch_json["name"], branch_json["day"])
        for choice_json in branch_json["choices"]:
            choice = Choice(branch, choice_json["direction"], choice_json["name"])
            route_ret = parse_route(route, choice_json["route"], depth + 1)
            choice.set_route(route_ret)
    
    return route

def parse_game_data(data_json):
    names = {}
    for name_json in data_json["names"]:
        names[name_json["id"].lower()] = Name(**name_json)
    game_tree = Tree(names)
    
    for route_json in data_json["routes"]:
        base_route = parse_route(None, route_json)
        game_tree.base_routes[base_route.name] = base_route
    
    return game_tree

def save_tree(filename, game_tree):
    with open(filename, "w") as f:
        json.dump(game_tree, f, cls = CustomEncoder, indent = 2)