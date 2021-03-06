from piece import Piece
from helpers import *

class Board:
    '''
    Initialize the Black/White list, store Piece instance in the list.
    Initialize weight for each features. Store each feature's value.
    '''
    def __init__(self):
        black = []
        white = []
        self.Pieces = [black, white]  # [black, white] list of Piece
        self.Range = (0, 8) # location should be in this range to be in board
        self.Corner = [(0,0),(0,7),(7,7),(7,0)]

    # Return a tuple of all features' value
    def get_features(self, color, phase_turns):
        n_alive, n_danger, n_edge, n_safe, n_moves = 0, 0, 0, 0, 0
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        enemy = 1 - color
        pieces = self.Pieces[color]
        for piece in pieces:
            # Feature1: Left piece number of one color
            n_alive += 1
            # Feature5: number of pieces that could not be killed.
            if is_safe(self, color, piece.location):
                n_safe += 1
            # Feature2: The number of pieces that could be killed in 1 move. 
            # Return the number.
            else:
                for d in directions:
                    neighbor_location = add(piece.location, d)
                    neighbor_status = get_status(self, neighbor_location)
                    # Neighbor is empty
                    if neighbor_status == enemy or neighbor_status == CORNER:
                        other_neighbor_location = add(piece.location, mul(d, -1))
                        other_neighbor_status = get_status(
                            self, other_neighbor_location)
                        # have empty spot
                        if other_neighbor_status == EMPTY:
                            # PLACING or MOVING
                            if phase_turns == -1 or can_move_to(self, enemy, 
                                other_neighbor_location, d):
                                n_danger += 1
            # Feature3: The number of pieces that locate at edges.(MOVING only)
            if phase_turns != -1:
                x, y = piece.location
                edges = self.Corner[1]
                if x in edges or y in edges:
                    n_edge += 1
        # placing phase, using 3 features.
        if phase_turns == -1:
            return [n_alive, -n_danger, n_safe]
        # moving phase, using 5 features.
        else:
            f_edge = get_f_edge(n_edge, phase_turns)
            # Feature4: The numbers that could move. (MOVING only)
            f_moves = len(self.possible_moves(color))
            return [n_alive, -n_danger, -f_edge, f_moves, n_safe]

    # Update the board with one movement of piece.
    def move_piece(self, action, color):
        # update the moved piece in the list.
        for piece in self.Pieces[color]:
            if piece.location == action[0]:
                piece.location = action[1]
        # eliminate any pieces if possible
        self.start_fight(action[1], color)
        return self

    # Update the board with one placement of piece.
    def place_piece(self, action, color):
        piece = Piece(action, color)
        self.Pieces[color].append(piece)
        self.start_fight(action, color)

    def start_fight(self, my_location, my_color):
        # check if kills others
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        friend = my_color
        enemy = 1 - my_color
        # check if it kills others
        for direction in directions:
            neighbor_location = add(my_location, direction)
            neighbor_status = get_status(self, neighbor_location)
            # neighbor is different color
            if neighbor_status == enemy:
                opposite_location = add(neighbor_location, direction)
                opposite_status = get_status(self, opposite_location)
                if opposite_status == friend or opposite_status == CORNER:
                    self.eliminate(neighbor_location, enemy)
        # check if it is killed
        for direction in directions:
            neighbor_location = add(my_location, direction)
            neighbor_status = get_status(self, neighbor_location)
            # neighbor is different color
            if neighbor_status == enemy:
                other_neighbor_location = add(my_location, mul(direction, -1))
                other_neighbor_status = get_status(self, other_neighbor_location)
                if other_neighbor_status==enemy or other_neighbor_status==CORNER:
                    self.eliminate(my_location, my_color)
                    break

    # Eliminate a piece from the board
    def eliminate(self, location, color):
        for piece in self.Pieces[color]:
            if piece.location == location:
                self.Pieces[color].remove(piece)
                break

    # Eliminate pieces located at the edge, Update the Black and White list.
    def eliminate_edge_piece(self):
        edges = self.Corner[1]
        for color in [BLACK, WHITE]:
            removed_pieces = []
            for piece in self.Pieces[color]:
                x, y = piece.location
                if (x in edges) and not (y in edges):
                    removed_pieces.append(piece.location)
                if (y in edges) and not (x in edges):
                    removed_pieces.append(piece.location)
            if removed_pieces:
                for piece in removed_pieces:
                    self.eliminate(piece, color)

    # for debug
    def print_board(self):
        for color in [0 ,1]:
            pieces = []
            for piece in self.Pieces[color]:
                pieces.append(piece.location)
            print(color, pieces)

    # Shrink the board when turns in [128,192]
    def shrink_board(self, turns):
        self.eliminate_edge_piece()
        # update board info
        self.Range = add(self.Range, (1, -1))
        if turns == 128:
            self.Corner = [(1, 1), (1, 6), (6, 6), (6, 1)]
        elif turns == 192:
            self.Corner = [(2, 2), (2, 5), (5, 5), (5, 2)]

        # corner elimination
        # add corner and eliminate its neighbor if possible
        removed_pieces = [[],[]]
        # check each corner from the top left anticlockwise
        for corner in self.Corner:
            # find the corner from every pieces in the list
            for color in [BLACK, WHITE]:
                for piece in self.Pieces[color]:
                    # remove the piece at corner
                    if piece.location == corner:
                        removed_pieces[color].append(piece.location)
            # the corner kills its neighbor
            for d in self.get_dd(corner):
                neighbor_location = add(corner, d)
                neighbor_status = get_status(self, neighbor_location)
                opposite_location = add(neighbor_location, d)
                opposite_status = get_status(self, opposite_location)
                # The two adjacent location have pieces with opposite color
                # status can only be EMPTY(-1) BLACK(0) WHITE(1)
                if neighbor_status + opposite_status == 1:  
                    removed_pieces[neighbor_status].append(neighbor_location)
        for color in [0, 1]:
            if removed_pieces[color]:
                for location in removed_pieces[color]:
                    self.eliminate(location, color)

    # Return the 2 directions of a corner which points toward the board
    def get_dd(self, location):
        dd = []
        c, r = location
        if c == self.Range[0]:
            dd.append((1, 0))
        else:
            dd.append((-1, 0))
        if r == self.Range[0]:
            dd.append((0, 1))
        else:
            dd.append((0, -1))
        return dd

    # Return a list of all possible move action [((),()), ]
    def possible_moves(self, color):
        possible_moves = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        enemy = 1 - color
        for piece in self.Pieces[color]:
            for d in directions:
                neighbor_location = add(piece.location,d)
                neighbor_status = get_status(self, neighbor_location)
                # Can move?
                if neighbor_status == EMPTY:
                    possible_moves.append((piece.location, neighbor_location))
                # What about jump?
                elif neighbor_status == enemy:
                    opposite_location = add(neighbor_location,d)
                    opposite_status = get_status(self, opposite_location)
                    if opposite_status == EMPTY:
                        possible_moves.append((piece.location, opposite_location))
        return possible_moves

    # Return the winner if the game end
    def game_ended(self):
        n_black = len(self.Pieces[BLACK])
        n_white = len(self.Pieces[WHITE])
        # tie
        if n_black < 2 and n_white < 2:
            return 3
        # white wins
        if n_black < 2:
            return WHITE + 1
        # black wins
        if n_white < 2:
            return BLACK + 1
        return 0