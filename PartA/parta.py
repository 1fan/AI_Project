from Node import *
from judge import *


def is_empty(my_list):
    if not my_list:
        return True
    return False


# return the node after making the move from start to end, do NOT kill a dead black piece yet
def create_new_node(parent, start, end):
    new_route = list(parent.route)
    new_route.append([start, end])
    new_white = list(parent.white)
    new_white.remove(start)
    new_white.append(end)
    new = Node(parent.black, new_white, new_route, parent.cost + 1)
    return new


def read_input():
    for i in range(9):
        if i == 8:
            action = input().strip()
            if action == "Moves":
                return 1
            elif action == "Massacre":
                return 2
            else:
                print("Invalid Command")
                exit(-1)
        else:
            c = 0
            for ch in input().strip():
                if ch == "O":
                    white.append((c, i))
                elif ch == "@":
                    black.append((c, i))
                if ch != " ":
                    c += 1


if __name__ == "__main__":
    black = []  # list of all black pieces
    white = []  # list of all white pieces

    # Task Moves
    if read_input() == 1:
        node0 = Node(black, white, [], 0)
        print_moves(node0)

    # Task Massacre
    else:
        PQ = []                                 # A priority queue of nodes sorting by f (f = cost + heuristic)
        node0 = Node(black, white, [], 0)       # initial state
        PQ.append(node0)

        all_b_are_killed = False
        current_node = node0
        while not all_b_are_killed:
            target_b = current_node.black[0]
            target_b_is_killed = False

            # Make movable moves of every white piece
            for W0 in current_node.white:
                w_list = get_coordinates_after_possible_moves(current_node, W0)
                if w_list:
                    for W in w_list:
                        new_node = create_new_node(current_node, W0, W)

                        # Check if there are black pieces other than the target piece that could be kill by this move
                        kill_by_accident = False
                        for b in new_node.black:
                            if b != target_b and is_killed(new_node, b):
                                kill_by_accident = True
                                break

                        # forget about this move and try next move in W_list
                        if kill_by_accident:
                            break

                        if is_killed(new_node, target_b):
                            target_b_is_killed = True
                            print_massacre(new_node.route)

                            # Update newNode by deleting the killed black piece
                            new_node.black.remove(target_b)
                            new_node.route.clear()

                            # Update PQ by replacing it with new_node as the only item
                            del PQ[:]
                            PQ.append(new_node)
                            break
                        else:
                            PQ.append(new_node)
                            PQ = sorted(PQ, key=lambda Node: Node.f)
                    if target_b_is_killed:
                        break
            # Check is all killed
            current_node = PQ.pop(0)
            all_b_are_killed = is_empty(current_node.black)

