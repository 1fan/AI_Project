import numpy as np
from board import Board
from helpers import *
from node import Node
import copy

class Player:
    # initialize: phase_turns, board, phase, color:BLACK, WHITE = 0, 1
    def __init__(self, colour):
        match_color = {'black': 0, 'white': 1}
        self.color = match_color[colour]
        self.phase = "placing"
        self.phase_turns = 0
        self.board = Board()
        BLACK_POSSIBLE_PLACE = []
        WHITE_POSSIBLE_PLACE = []
        self.POSSIBLE_PLACE = [BLACK_POSSIBLE_PLACE, WHITE_POSSIBLE_PLACE]
        self.initLegalPlace()

    def initLegalPlace(self):
        for c in range(0,8):
            for r in range(2,8):
                self.POSSIBLE_PLACE[BLACK].append((c, r))
        self.POSSIBLE_PLACE[BLACK].remove((0, 7))
        self.POSSIBLE_PLACE[BLACK].remove((7, 7))
        for c in range(0,8):
            for r in range(0,6):
                self.POSSIBLE_PLACE[WHITE].append((c,r))
        self.POSSIBLE_PLACE[WHITE].remove((0, 0))
        self.POSSIBLE_PLACE[WHITE].remove((7, 0))

    def action(self, turns):
        if self.phase == "placing":
            Best_Place = self.best_place()
            self.remove_from_possible_place(Best_Place)
            self.board.place_piece(Best_Place, self.color)
            self.update_turns()
            return Best_Place

        if self.phase == "moving":
            # shrink the board before my move
            if self.phase_turns in [128, 192]:
                self.board.shrink_board(self.phase_turns)
            # Give a best move
            Best_Move = self.best_move()

            # Make the move on my board
            self.board.move_piece(Best_Move, self.color)
            self.phase_turns += 1

            # shrink the board after my move
            if self.phase_turns in [128, 192]:
                self.board.shrink_board(self.phase_turns)

            return Best_Move

    def update(self, action):
        # adjust opponent's piece
        # if action is a nested tuple --> it is a 'move'; else --> it is a 'place'
        if action:
            enemy_color = 1 - self.color
            self.update_turns()
            # moving phase
            if isinstance(action[0], tuple):
                self.board.move_piece(action, enemy_color)
            # placing phase
            else:
                self.board.place_piece(action, enemy_color)
                self.remove_from_possible_place(action)

    def update_turns(self):
        self.phase_turns += 1
        if self.phase == "placing" and self.phase_turns == 24:
            self.phase = "moving"
            self.phase_turns = 0


    def remove_from_possible_place(self, location):
        c ,r = location
        if r in range(2, 8):
            self.POSSIBLE_PLACE[BLACK].remove(location)
        if r in range(0, 6):
            self.POSSIBLE_PLACE[WHITE].remove(location)

    # Make decision of move a piece


    # Make decision of move a piece
    def best_move(self):
        # MINIMAX
        depth_limit = self.get_depth()
        this_board = copy.deepcopy(self.board)
        root = Node(depth_limit, self.color, this_board, None, self.color)
        best_val = -1000
        best_move = 0
        if root.children is None:
            return None
        for i in range(len(root.children)):
            child = root.children[i]
            val = child.minmax(depth_limit - 1, self.phase_turns + 1)
            # update best value and move for min max
            if val > best_val:
                best_val = val
                best_move = i
        return root.children[best_move].action

    # Make decision of placing a piece, call Board.placePiece() function to update the board.
    def best_place(self):
        # EVALUATION
        Possible_Places = self.POSSIBLE_PLACE[self.color]
        max_e = -np.inf
        best_place = 0
        for i in range(len(Possible_Places)):
            # new_Pieces = self.board.Pieces
            new_board = copy.deepcopy(self.board)
            new_board.place_piece(Possible_Places[i], self.color)
            node = Node(0, self.color, new_board, None, self.color)
            # should have a different feature function
            this_e = node.get_e(-1)
            if this_e > max_e:
                max_e = this_e
                best_place = i
        return Possible_Places[best_place]

    def get_depth(self):
        if self.board.Range[1] == 8:
            return 2
        return 3