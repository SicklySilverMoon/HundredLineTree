import json
from json import JSONEncoder
import sys
import os
from string import whitespace

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
        self.choices = {"left": None, "right": None}
        
        self.parent.branch = self
        
    def set_choice(self, choice):
        self.choices[choice.direction] = choice
    
    def as_dict(self):
        d = {}
        d["name"] = self.name if self.name else "[UNKNOWN]"
        d["day"] = self.day if self.day else -1
        choices = []
        if self.choices["left"]:
            choices.append(self.choices["left"].as_dict())
        else:
            choices.append({})
        if self.choices["right"]:
            choices.append(self.choices["right"].as_dict())
        else:
            choices.append({})
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
        if self.branch:
            d["branch"] = self.branch.as_dict()
        if self.events:
            d["events"] = []
            for event in self.events:
                d["events"].append(event.as_dict())
            #print (d["events"])
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

def whitespace_start(string):
    return string.startswith(tuple(w for w in whitespace))

def parse_route(parent_route, route_json, depth = 0):
    #print(route_json)
    
    route = Route(parent_route, route_json["name"])
    
    events = []
    if "events" in route_json:
        for event_json in route_json["events"]:
            events.append(Event(event_json["name"], event_json["days"]))
        route.set_events(sort_by_days(events))
    
    deaths = {}
    if "deaths" in route_json:
        for death_json in route_json["deaths"]:
            deaths[death_json["id"].lower()] = (Death(death_json["id"], death_json["count"], death_json["days"]))
        route.set_deaths(deaths)
    
    #if depth == 0:
    #    print(route.name)
    if "branch" in route_json:
        branch_json = route_json["branch"]
        branch = Branch(route, branch_json["name"], branch_json["day"])
        for choice_json in branch_json["choices"]:
            choice = Choice(branch, choice_json["direction"], choice_json["name"])
            route_ret = parse_route(route, choice_json["route"], depth + 1)
            choice.set_route(route_ret)
    
    #if depth == 0:
    #    print(route.name)
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


def check_name_id_exists(game_tree, name_id):
    for name in game_tree.names.values():
        if name_id == name.id:
            return True
    return False

def sort_by_days(array):
    return sorted(array, key = lambda item: item.days[0])

#todo: my god split these out to multiple files
def edit_death(game_tree, death):
    while True:
        print(f"You are editing death with id {death.id},")
        response = input("Edit target (t), edit count (c), edit days (d), or 'x' to exit: ")
        match response:
            case 't':
                print("Available death targets are: ")
                for name in game_tree.names:
                    print(f"{game_tree.names[name].id}: {game_tree.names[name].full}", end = ", ")
                response = input("Selection: ").lower().strip()
                while not check_name_id_exists(game_tree, response):
                    response = input("Selection: ").lower().strip()
                death.id = response
            case 'c':
                response = input("Enter the times this character has died on this specific route after branches: ")
                try:
                    death.count = int(response)
                except ValueError:
                    pass
            case 'd':
                response = input("Enter a comma seperated list of days that this character has died on on this specific route after branches: ")
                days_str = response.split(',')
                days = []
                for day in days_str:
                    try:
                        days.append(int(day.strip()))
                    except ValueError:
                        pass
                death.days = sorted(days)
            case 'x':
                return

def edit_deaths(game_tree, route):
    deaths = route.deaths
    while True:
        print(f"\nDeaths in route \"{route.name}\":")
        for key in deaths:
            death = deaths[key]
            print(f"  ID: \"{death.id}\". Name: {game_tree.names[death.id].full}. Times died (additive): {death.count}. Days died on: {death.days}.")
        response = input("Edit (e) death, remove (r) death, add (a) death, or 'x' to exit: ")
        match response:
            case 'e':
                if len(deaths) == 0:
                    print("No deaths to edit")
                    pass
                response = input("ID to edit: ").lower().strip()
                while response not in deaths:
                    response = input("ID to edit: ").lower().strip()
                edit_death(game_tree, deaths[response])
                
            case 'r':
                if len(deaths) == 0:
                    print("No deaths to remove")
                    pass
                response = input("ID to remove: ").lower().strip()
                while response not in deaths:
                    response = input("ID to remove: ").lower().strip()
                del deaths[response]
                
            case 'a':
                id = input("ID to insert: ").lower().strip()
                while not check_name_id_exists(game_tree, id):
                    id = input("ID to insert: ").lower().strip()
                count = -1
                while count == -1:
                    try:
                        count = int(input("Enter the number of times this character has died in this specific route: "))
                    except ValueError:
                        pass
                days_str = input("Enter a comma seperated list of days that this character has died on on this specific route after branches: ")
                days_str = days_str.split(',')
                days = []
                for day in days_str:
                    try:
                        days.append(int(day.strip()))
                    except ValueError:
                        pass
                deaths[id] = Death(id, count, days)
                
            case 'x':
                route.deaths = deaths
                return
    
def edit_event(event):
    while True:
        print(f"You are editing event on day(s) {event.days} with desc: {event.name}")
        response = input("Edit days (d), edit desc (e) 'x' to exit: ")
        match response:
            case 'e':
                desc = input("Enter the event description: ")
                event.name = desc
                
            case 'd':
                response = input("Enter a comma seperated list of days that this event has occured on in this specific route: ")
                days_str = response.split(',')
                days = []
                for day in days_str:
                    try:
                        days.append(int(day.strip()))
                    except ValueError:
                        pass
                event.days = sorted(days)
                
            case 'x':
                return

def edit_events(game_tree, route):
    events = route.events
    while True:
        print(f"\nEvents in route \"{route.name}\":")
        for i in range(len(events)):
            event = events[i]
            print(f"  {i}: Day(s) the event occured on: {event.days}. Desc: \"{event.name}\".")
        response = input("Edit (e) event, remove (r) event, add (a) event, or 'x' to exit: ")
        match response:
            case 'e':
                if len(events) == 0:
                    print("No events to edit")
                    pass
                response = -1
                while response >= len(events) or response < 0:
                    try:
                        response = int(input("Index to edit: "))
                    except ValueError:
                        pass
                edit_event(events[response])
                
            case 'r':
                if len(events) == 0:
                    print("No events to remove")
                    pass
                response = -1
                while response >= len(events) or response < 0:
                    try:
                        response = int(input("Index to remove: "))
                    except ValueError:
                        pass
                del events[response]
                
            case 'a':
                name = input("Enter the event description: ")
                days_str = input("Enter a comma seperated list of days that this event takes place on: ").split(',')
                days = []
                for day in days_str:
                    try:
                        days.append(int(day.strip()))
                    except ValueError:
                        pass
                days = sorted(days)
                event = Event(name, days)
                events.append(event)
                events = sort_by_days(events)
            case 'x':
                route.events = events
                return

def edit_branch(game_tree, route):
    while True:
        if route.branch:
            print(f"\nThis route has a branch with choice \"{route.branch.name}\" on day {route.branch.day} and options:")
            print(f"  left side: \"{route.branch.choices["left"].name}\"")
            print(f"  right side: \"{route.branch.choices["right"].name}\"")
            response = input("Edit branch choice (c), edit branch day (d), edit/descend into left side (l), edit/descend into right side (r), or 'x' to exit: ")
            match response:
                case 'c':
                    route.branch.name = input("Enter new choice name: ")
                case 'd':
                    day = -1
                    while day == -1:
                        try:
                            day = int(input("Enter the day this branch occurs on: "))
                        except ValueError:
                            pass
                    route.branch.day = day
                case 'l' | 'r':
                    response2 = input("Edit label (e) or desend (d): ")
                    if response2 == 'e':
                        label = input("Enter new label: ")
                        route.branch.choices["left" if response == 'l' else "right"].name = label
                    elif response2 == 'd':
                        edit_recurse(game_tree, route.branch.choices["left" if response == 'l' else "right"].route)
                        return
                case 'x':
                    return
        else:
            print("This route has no branch")
            response = input("Add branch (a), or 'x' to exit: ")
            match response:
                case 'a':
                    name = input("Input branch choice: ")
                    left = input("Input left side label: ")
                    right = input("Input right side label: ")
                    day = int(input("Input day: "))
                    branch = Branch(route, name, day)
                    choice_left = Choice(branch, "left", left)
                    choice_right = Choice(branch, "right", right)
                    route_left = Route(route, route.name + " LEFT BRANCH")
                    route_right = Route(route, route.name + " RIGHT BRANCH")
                    choice_left.set_route(route_left)
                    choice_right.set_route(route_right)
                    route.set_branch(branch)
                case 'x':
                    return

def edit_recurse(game_tree, route):
    while True:
        print(f"\nRoute title: \"{route.name}\"")
        if len(route.deaths) > 0:
            print("Deaths:")
            for key in route.deaths:
                death = route.deaths[key]
                print(f"  Name: {game_tree.names[death.id].full}. Times died: {death.count}. Days died on: {death.days}.")
        
        if len(route.events) > 0:
            print(f"There are {len(route.events)} events on this route occuring on day collections: ", end = "")
            for event in route.events[ : -1]:
                print(event.days, end = ", ")
            print(route.events[-1].days)
        
        if route.branch:
            print(f"This route has a branch choice with title \"{route.branch.name}\", and options \"{route.branch.choices["left"].name}\" (left), and \"{route.branch.choices["right"].name}\" (right) on day {route.branch.day}")
        print("You may edit/add deaths (d), edit/add events (e), or edit/add a branch (b), change the title (t), or 'x' to return to the previous route")
        response = input("Selection: ")
        match response:
            case 'd':
                edit_deaths(game_tree, route)
            case 'e':
                edit_events(game_tree, route)
            case 'b':
                edit_branch(game_tree, route)
            case 't':
                response = input("Input new branch title: ")
                route.name = response
            case 'x':
                return
                
            case 'ld' | 'rd': #hidden for now, allows instant descent from route base
                branch = route.branch
                if not branch:
                    continue
                if response == 'ld':
                    new_route = branch.choices["left"].route
                else:
                    new_route = branch.choices["right"].route
                if new_route:
                    edit_recurse(game_tree, new_route)
            case 's': #also hidden, save the file
                save_tree(sys.argv[3], game_tree)

def edit_names(game_tree):
    while True:
        print("\nNames in this game are:")
        for name in game_tree.names.values():
            print(f"  ID: {name.id}. Name: \"{name.full}\"")
        response = None
        while response not in game_tree.names:
            response = input("Enter the name id you want to edit or 'x' to exit: ").strip().lower()
            if response == 'x':
                return
        
        name = game_tree.names[response]
        print(f"\n{name.id}:")
        print(f"  first name: \"{name.first if name.first else "[UNKNOWN]"}\"")
        print(f"  last name: \"{name.last if name.last else "[UNKNOWN]"}\"")
        print(f"  full name: \"{name.full if name.full else "[UNKNOWN]"}\"")
        print(f"  position: \"{name.position if name.position else "[UNKNOWN]"}\"")
        print(f"  title: \"{name.title if name.title else "[UNKNOWN]"}\"")
        print(f"  website title: \"{name.web_title if name.web_title else "[UNKNOWN]"}\"")
        response = input("Insert/add first (f), last (l), full (u), position (p), title (t), web title (w), 'x' to exit: ")
        item = ""
        match response:
            case 'f':
                item = "first name"
            case 'l':
                item = "last name"
            case 'u':
                item = "full name"
            case 'p':
                item = "position"
            case 't':
                item = "title"
            case 'w':
                item = "website title"
            case 'x':
                continue
            case '_':
                continue
        text = input(f"Enter this character's {item}: ")
        match response:
            case 'f':
                name.first = text
            case 'l':
                name.last = text
            case 'u':
                name.full = text
            case 'p':
                name.position = text
            case 't':
                name.title = text
            case 'w':
                name.web_title = text

def edit(game_tree):
    while True:
        string = f"\nYou can edit {len(game_tree.base_routes)} base routes:\n"
        i = 1
        keys = list(game_tree.base_routes.keys())
        for i in range(len(keys)):
            key = keys[i]
            route = game_tree.base_routes[key]
            string += f"  {i}: {route.name}\n"
        string += "Select a number, 'n' to edit names, or 'x' to exit: "
        response = input(string)
        try:
            response = int(response)
            edit_recurse(game_tree, game_tree.base_routes[keys[response]])
        except ValueError:
            if response == 'n':
                edit_names(game_tree)
            else:
                print("Saving file and exiting")
                return

def save_tree(filename, game_tree):
    with open(filename, "w") as f:
        json.dump(game_tree, f, cls = CustomEncoder, indent = 2)


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
                death.days += parent_death.days
            deaths[death_key] = death
    if len(deaths) > 0:
        for death in deaths.values():
            print(names[death.id].full, "died", death.count, "time(s)", "on day(s)", str(death.days)[1 : -1], end = "; ")
        print("")
    
    if route.branch:
        print((" " * ((depth) * multiplier)) + f"Decide: {route.branch.choices["left"].name} on {route.branch.name:}")
        print_routes(names, route.branch.choices["left"].route, deaths, depth + 1)
        print((" " * ((depth) * multiplier)) + f"Decide: {route.branch.choices["right"].name} on {route.branch.name:}")
        print_routes(names, route.branch.choices["right"].route, deaths, depth + 1)

def print_tree(game_tree):
        for route_key in game_tree.base_routes:
            print_routes(game_tree.names, game_tree.base_routes[route_key])
            print("")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} json_file [(display|edit output_json)]")
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        data = json.load(f)
    
    game_tree = parse_game_data(data)
    
    if len(sys.argv) >= 3:
        if sys.argv[2].strip().lower() == "display":
            print_tree(game_tree)
        elif sys.argv[2].strip().lower() == "edit":
            if len(sys.argv) < 4:
                print("edit on command line requires output file name!")
                sys.exit(1)
            edit(game_tree)
            save_tree(sys.argv[3], game_tree)

    else:
        response = input("1 to display file, 2 to edit: ")
        if int(response) == 1:
            print_tree(game_tree)
        elif int(response) == 2:
            edit(game_tree)
            save_tree(input("Input filename to save to: "), game_tree)
