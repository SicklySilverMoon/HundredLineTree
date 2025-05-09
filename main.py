import sys
import json
from parse_game import parse_game_data, save_tree
from utils import check_name_id_exists, sort_by_days
from edit_game import edit
from print_game import print_tree

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
