from utils import check_name_id_exists, sort_by_days

def get_int(prompt):
    num = None
    while not num:
        try:
            num = int(input(prompt))
        except ValueError:
            pass
    return num

def get_from_set(prompt, the_set, ls = True):
    response = None
    while response not in the_set:
        response = input(prompt)
        if ls:
            response = response.strip().lower()
    return response

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
                    continue
                response = get_from_set("ID to edit: ", deaths)
                edit_death(game_tree, deaths[response])
                
            case 'r':
                if len(deaths) == 0:
                    print("No deaths to remove")
                    continue
                response = get_from_set("ID to remove: ", deaths)
                del deaths[response]
                
            case 'a':
                id = input("ID to insert: ").lower().strip()
                while not check_name_id_exists(game_tree, id):
                    id = input("ID to insert: ").lower().strip()
                count = get_int("Enter the number of times this character has died in this specific route: ")
                days_str = input("Enter a comma seperated list of days that this character has died on on this specific route after branches: ")
                days_str = days_str.split(',')
                days = []
                for day in days_str:
                    try:
                        days.append(int(day.strip()))
                    except ValueError:
                        pass
                deaths[id] = Death(id, count, days)
                deaths = {d.id : d for d in sort_by_days([d for d in deaths.values()])}
                route.set_deaths(deaths)
                
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
                    continue
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
                    continue
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
            choices = route.branch.choices
            for i in range(len(choices)):
                choice = choices[i]
                print(f"  {i}: {choice.direction} side: \"{choice.name}\"")
            response = input("Edit branch choice (c), edit branch day (d), add new choice (a), edit/descend into choice (index), or 'x' to exit: ")
            match response:
                case 'c':
                    route.branch.name = input("Enter new choice name: ")
                case 'd':
                    day = get_int("Enter the day this branch occurs on: ")
                    route.branch.day = day
                case 'a':
                    direction = input("Input direction: ").lower().strip()
                    label = input("Input choice label: ")
                    choice = Choice(route.branch, direction, label)
                    route_new = Route(route.branch, route.name + f" {direction.upper()} BRANCH")
                    choice.set_route(route_new)
                case 'x':
                    return
                case _:
                    try:
                        index = int(response)
                        choice = choices[index]
                        response2 = input("Edit label (e), desend (d), remove (r), or 'x' to exit: ")
                        if response2 == 'e':
                            label = input("Enter new label: ")
                            choice.name = label
                        elif response2 == 'd':
                            edit_recurse(game_tree, choice.route)
                            return
                        elif response2 == 'r':
                            del choices[index]
                        elif response2 == 'x':
                            continue
                    except ValueError:
                        continue

        else:
            print("This route has no branch")
            response = input("Add branch (a), or 'x' to exit: ")
            match response:
                case 'a':
                    name = input("Input branch choice: ")
                    day = int(input("Input day: "))
                    branch = Branch(route, name, day)
                    num_choices = get_int("Input number of choices: ")
                    for i in range(num_choices):
                        direction = input("Input direction: ").lower().strip()
                        label = input("Input choice label: ")
                        choice = Choice(branch, direction, label)
                        route_new = Route(route, route.name + f" {direction.upper()} BRANCH")
                        choice.set_route(route_new)
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
            string = f"This route has a branch choice with title \"{route.branch.name}\", and options "
            for choice in route.branch.choices:
                string += f"\"{choice.name}\" ({choice.direction}), "
            string += f"on day {route.branch.day}"
            print(string)
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
                response = input("Input new route/chapter title: ")
                route.name = response
            case 'x':
                return
                
            case 'ld' | 'rd' | 'td': #hidden for now, allows instant descent from route base
                branch = route.branch
                if not branch:
                    continue
                values = {"ld": "left", "rd": "right", "td": "top"}
                for choice in branch.choices:
                    if choice.direction == values[response]:
                        new_route = choice.route
                        break
                if new_route:
                    edit_recurse(game_tree, new_route)
            case 's': #also hidden, save the file
                save_tree(sys.argv[3], game_tree)

def edit_name(name):
    while True:
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
                return
            case _:
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


def edit_names(game_tree):
    while True:
        print("\nNames in this game are:")
        for name in game_tree.names.values():
            print(f"  ID: {name.id}. Name: \"{name.full}\"")
        response = get_from_set("Enter the name id you want to edit, 'a' to add a new name, or 'x' to exit: ", list(game_tree.names.keys()) + ['x', 'a'])
        if response == 'x':
            return
        elif response == 'a':
            response = input("Enter the new name id: ")
            game_tree.names[response] = Name(id = response)
        else:
            name = game_tree.names[response]
            edit_name(name)

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
