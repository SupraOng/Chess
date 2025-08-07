# TODO: check/checkmate detection, turn management

import pygame as pg
import copy
from piece import Piece

class Board:
    def __init__(self, screen):
        self.screen = screen

        self.dim = 8
        self.board = []

        self.offset = 50
        self.square_size = 800 // self.dim

        self.light_color = (41.6, 44.7, 51)
        self.dark_color = (14.5, 17.3, 22.4)
        self.highlight_color = (0, 255, 0)

        self.starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

        self.selected_piece = None
        self.selected_coords = None

        self.color_to_move = Piece.white

        self.promoting = False
        self.promotion_square = None
        self.promotion_color = None

        self.last_move = None

        self.checkmate = False

        self.draw_pieces = False

        self.create_board()
        if self.draw_pieces:
            self.place_pieces_from_fen(self.starting_fen)
        

    def create_board(self):
        for file in range(self.dim):
            self.board.append([])
            for rank in range(self.dim):
                self.board[file].append(0)

    def create_graphical_board(self):
        for file in range(self.dim):
            for rank in range(self.dim):

                is_light_square = (file + rank) % 2 == 0

                square_color = self.light_color if is_light_square else self.dark_color
                square_pos = (file * self.square_size, rank * self.square_size + self.offset)
                
                pg.draw.rect(self.screen, square_color, pg.Rect(square_pos, (self.square_size, self.square_size)))

    def place_pieces_from_fen(self, fen):
        piece_map = {
            'p': Piece.pawn,
            'r': Piece.rook,
            'n': Piece.knight,
            'b': Piece.bishop,
            'q': Piece.queen,
            'k': Piece.king
        }

        ranks = fen.split('/')

        for rank_index, row in enumerate(ranks):
            file = 0
            for char in row:
                if char.isdigit():
                    file += int(char)
                else:
                    color = Piece.white if char.isupper() else Piece.black
                    piece_type = piece_map[char.lower()]
                    x = file * self.square_size
                    y = rank_index * self.square_size + self.offset
                    piece = Piece(self.screen, piece_type, color, (x, y))
                    if self.draw_pieces:
                        piece.display_piece()
                    self.board[file][rank_index] = piece
                    file += 1

    def update_piece_positions(self):
        for file in range(self.dim):
            for rank in range(self.dim):
                piece = self.board[file][rank]
                if piece != 0:
                    x = file * self.square_size
                    y = rank * self.square_size + self.offset
                    piece.position = (x, y)
                    if self.draw_pieces:
                        piece.display_piece()

    def draw(self):
        self.create_graphical_board()
        self.update_piece_positions()

    def handle_click(self, mousex, mousey):

        if self.checkmate:
            return

        # Determine which square was clicked
        file = mousex // self.square_size
        # Subtract self.offset from mousey before dividing to get the correct rank
        rank = (mousey - self.offset) // self.square_size

        
        # If there's no piece selected and the clicked square has a piece, select it
        # If there's a piece selected, move it to the clicked square
        if self.selected_piece == None and self.board[file][rank] != 0:
            self.selected_piece = self.board[file][rank]
            self.selected_coords = (file, rank)

            # Only select the current color to move's pieces
            if self.selected_piece.color != self.color_to_move:
                self.selected_piece = None
                self.selected_coords = None
                current_color = "white" if self.color_to_move == 8 else "black"
                print("waiting for " + current_color + " to move")
                return

        elif self.selected_piece != None:

            valid_moves = self.get_valid_moves(self.selected_piece)

            if not self.promoting:
                if (file, rank) in valid_moves:
                    
                    # Store the old file and rank in variable, and set where the piece used to be to 0
                    old_file, old_rank = self.selected_coords
                    self.board[old_file][old_rank] = 0

                    # Handle Castling Rook Move
                    if self.selected_piece.piece_type == Piece.king and not self.selected_piece.has_moved:
                        back_rank = 7 if self.selected_piece.color == Piece.white else 0

                        # Kingside
                        if (file, rank) == (6, back_rank):
                            rook = self.board[7][back_rank]
                            self.board[5][back_rank] = rook
                            self.board[7][back_rank] = 0
                            rook.position = (5 * self.square_size, back_rank * self.square_size)
                            rook.has_moved = True
                        
                        # Queenside
                        if (file, rank) == (2, back_rank):
                            rook = self.board[0][back_rank]
                            self.board[3][back_rank] = rook
                            self.board[0][back_rank] = 0
                            rook.position = (3 * self.square_size, back_rank * self.square_size)

                    # Handle pawn special moves
                    if self.selected_piece.piece_type == Piece.pawn:

                        # Promotion
                        promote_rank = 0 if self.selected_piece.color == Piece.white else 7

                        if rank == promote_rank:
                            self.promoting = True
                            self.promotion_square = (file, rank)
                            self.promotion_color = self.selected_piece.color
                            
                            self.board[file][rank] = self.selected_piece
                            self.selected_piece = None
                            self.selected_coords = None
                            return

                        # En passant capture
                        if file != old_file and self.board[file][rank] == 0:
                            captured_rank = old_rank
                            self.board[file][captured_rank] = 0


                        
                    
                    # Set the new pieces location based on what square the player clicked.
                    self.board[file][rank] = self.selected_piece
                    self.selected_piece.has_moved = True
                    self.selected_piece.position = (file * self.square_size, rank * self.square_size + self.offset)

                    self.selected_piece = None
                    self.selected_coords = None

                    self.last_move = (old_file, old_rank, file, rank)
                    print(self.last_move)

                    self.switch_turns()

                    if self.is_checkmate(self.color_to_move):
                        self.checkmate = True
                        print("CHECKMATE")
                    

                else:
                    print("Invalid move for the selected piece.")
                    self.selected_piece = None
                    self.selected_coords = None
            else:
                print(f"{self.promotion_color} needs to promote first!")
            
        

    def switch_turns(self):
        # Switch turns
        if self.color_to_move == Piece.white:
            self.color_to_move = Piece.black
            print("it is now blacks turn")
        else:
            self.color_to_move = Piece.white
            print("it is now whites turn")

    def get_valid_moves(self, piece):
        valid_moves = []

        file = piece.position[0] // self.square_size
        # Subtract self.offset from y before dividing to get the correct rank
        rank = (piece.position[1] - self.offset) // self.square_size

        
        if piece.piece_type == Piece.pawn:
            self.pawn_valid_moves(file, rank, piece, valid_moves)
        
        if piece.piece_type == Piece.knight:
            self.knight_valid_moves(file, rank, piece, valid_moves)
            
        
        if piece.piece_type == Piece.rook:
            self.rook_valid_moves(file, rank, piece, valid_moves)
            
        
        if piece.piece_type == Piece.bishop:
            self.bishop_valid_moves(file, rank, piece, valid_moves)
        
        if piece.piece_type == Piece.queen:
            self.queen_valid_moves(file, rank, piece, valid_moves)
        
        if piece.piece_type == Piece.king:
            self.king_valid_moves(file, rank, piece, valid_moves)
        
        legal_moves = []
        for move in valid_moves:
            board_copy = self.copy_board()
            board_copy.move_piece((file, rank), move)
            if not board_copy.is_in_check(piece.color):
                legal_moves.append(move)

        return legal_moves
    
    def pawn_valid_moves(self, file, rank, piece, valid_moves):
        direction = -1 if piece.color == Piece.white else 1

        # One square forward
        next_rank = rank + direction
        if 0 <= next_rank < self.dim and self.board[file][next_rank] == 0:
            valid_moves.append((file, next_rank))
        
        # Two squares forward from starting position
        if not piece.has_moved:
            next_rank = rank + 2 * direction
            if 0 <= next_rank < self.dim and self.board[file][next_rank] == 0 and self.board[file][rank + direction] == 0:
                valid_moves.append((file, next_rank))
        
        # Capture left
        if file - 1 >= 0 and 0 <= next_rank < self.dim:
            target = self.board[file - 1][next_rank]
            if target != 0 and target.color != piece.color:
                valid_moves.append((file - 1, next_rank))
        
        # Capture right
        if file + 1 < self.dim and 0 <= next_rank < self.dim:
            target = self.board[file + 1][next_rank]
            if target != 0 and target.color != piece.color:
                valid_moves.append((file + 1, next_rank))

        # En Passant
        if self.last_move:
            from_file, from_rank, to_file, to_rank = self.last_move

            moved_piece = self.board[to_file][to_rank]
            if moved_piece.piece_type == Piece.pawn and abs(to_rank - from_rank) == 2:
                if abs(to_file - file) == 1 and to_rank == rank:
                    valid_moves.append((to_file, to_rank + direction))
        

    def rook_valid_moves(self, file, rank, piece, valid_moves):
        # Loop over all possible directions
            directions = [(1,0), (-1, 0), (0, 1), (0, -1)] # Right, left, down, up
            for dx, dy in directions:
                next_file, next_rank = file, rank
                while True:
                    next_file += dx
                    next_rank += dy

                    # If out of bounds of the board array, break the loop.
                    if not (0 <= next_file < self.dim and 0 <= next_rank < self.dim):
                        break
                    
                    # If the target piece is empty or occupied by the other color, move there.
                    target_piece = self.board[next_file][next_rank]
                    if target_piece == 0:
                        valid_moves.append((next_file, next_rank))
                    elif target_piece.color != piece.color:
                        valid_moves.append((next_file, next_rank))
                        break
                    else:
                        break

    def knight_valid_moves(self, file, rank, piece, valid_moves):
        # L-shaped moves
            knight_moves = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)
            ]

            # For each knight move, check if it's valid
            for dx, dy in knight_moves:
                next_file = file + dx
                next_rank = rank + dy

                if 0 <= next_file < self.dim and 0 <= next_rank < self.dim:
                    target_piece = self.board[next_file][next_rank]
                    # if the target square occupied by a piece of the same color, capture it.
                    # If the target square is empty, move there.
                    if target_piece == 0 or target_piece.color != piece.color:
                        valid_moves.append((next_file, next_rank))

    def bishop_valid_moves(self, file, rank, piece, valid_moves):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # Right down, Right up, left down, left up
            
        for dx, dy in directions:
            next_file, next_rank = file, rank
            while True:
                next_file += dx
                next_rank += dy

                if not (0 <= next_file < self.dim and 0 <= next_rank < self.dim):
                    break

                target_piece = self.board[next_file][next_rank]
                if target_piece == 0:
                    valid_moves.append((next_file, next_rank))
                elif target_piece.color != piece.color:
                    valid_moves.append((next_file, next_rank))
                    break
                else:
                    break

    def queen_valid_moves(self, file, rank, piece, valid_moves):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dx, dy in directions:
            next_file, next_rank = file, rank
            while True:
                next_file += dx
                next_rank += dy

                if not (0 <= next_file < self.dim and 0 <= next_rank < self.dim):
                    break

                target_piece = self.board[next_file][next_rank]
                if target_piece == 0:
                    valid_moves.append((next_file, next_rank))
                elif target_piece.color != piece.color:
                    valid_moves.append((next_file, next_rank))
                    break
                else:
                    break

    def king_valid_moves(self, file, rank, piece, valid_moves):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        # Basic King Movement
        for dx, dy in directions:
            next_file = file + dx
            next_rank = rank + dy
            if 0 <= next_file < self.dim and 0 <= next_rank < self.dim:
                target_piece = self.board[next_file][next_rank]
                if target_piece == 0 or target_piece.color != piece.color:
                    valid_moves.append((next_file, next_rank))
        
        # Castling
        if not piece.has_moved:
            back_rank = 7 if piece.color == Piece.white else 0
            
            # Kingside
            if all(self.board[f][back_rank] == 0 for f in (5, 6)):
                rook = self.board[7][back_rank]
                if rook != 0 and rook.piece_type == Piece.rook and not rook.has_moved:
                    valid_moves.append((6, back_rank))
            
            # Queenside
            if all(self.board[f][back_rank] == 0 for f in (1, 2, 3)):
                rook = self.board[0][back_rank]
                if rook != 0 and rook.piece_type == Piece.rook and not rook.has_moved:
                    valid_moves.append((2, back_rank))
    
    def is_in_check(self, color):
        # Get the king's position
        king_pos = None
        for file in range(self.dim):
            for rank in range(self.dim):
                piece = self.board[file][rank]
                if piece != 0 and piece.piece_type == Piece.king and piece.color == color:
                    king_pos = (file, rank)
                    break
        # Check opponent's pseudo-legal moves
        opponent_color = Piece.black if color == Piece.white else Piece.white
        for file in range(self.dim):
            for rank in range(self.dim):
                piece = self.board[file][rank]
                if piece != 0 and piece.color == opponent_color:
                    moves = self.get_pseudo_legal_moves(piece)
                    if king_pos in moves:
                        return True
        return False

    def get_pseudo_legal_moves(self, piece):
        valid_moves = []
        file = piece.position[0] // self.square_size
        rank = (piece.position[1] - self.offset) // self.square_size
        if piece.piece_type == Piece.pawn:
            self.pawn_valid_moves(file, rank, piece, valid_moves)
        if piece.piece_type == Piece.knight:
            self.knight_valid_moves(file, rank, piece, valid_moves)
        if piece.piece_type == Piece.rook:
            self.rook_valid_moves(file, rank, piece, valid_moves)
        if piece.piece_type == Piece.bishop:
            self.bishop_valid_moves(file, rank, piece, valid_moves)
        if piece.piece_type == Piece.queen:
            self.queen_valid_moves(file, rank, piece, valid_moves)
        if piece.piece_type == Piece.king:
            self.king_valid_moves(file, rank, piece, valid_moves)
        return valid_moves
    
    def is_checkmate(self, color):
        # If we're not in check, return
        # If we are in check, go through all possible moves of this color
        if not self.is_in_check(color):
            return False
        
        for file in range(self.dim):
            for rank in range(self.dim):
                piece = self.board[file][rank]
                if piece != 0 and piece.color == color:
                    moves = self.get_valid_moves(piece)
                    for move in moves:
                        board_copy = self.copy_board()
                        board_copy.draw_pieces = False
                        board_copy.move_piece((file, rank), move)
                        if not board_copy.is_in_check(color):
                            return False
        
        return True

    def copy_board(self):
        new_board = Board(self.screen)
        for file in range(self.dim):
            for rank in range(self.dim):
                piece = self.board[file][rank]
                if piece != 0:
                    new_piece = Piece(
                        self.screen,
                        piece.piece_type,
                        piece.color,
                        piece.position
                    )
                    new_piece.has_moved = piece.has_moved
                    new_piece.just_moved = piece.just_moved
                    new_board.board[file][rank] = new_piece
                else:
                    new_board.board[file][rank] = 0
        new_board.color_to_move = self.color_to_move
        # Copy other relevant attributes as needed
        return new_board
    
    def move_piece(self, from_pos, to_pos):
        from_file, from_rank = from_pos
        to_file, to_rank = to_pos

        piece = self.board[from_file][from_rank]

        self.board[to_file][to_rank] = piece
        self.board[from_file][from_rank] = 0
        if piece:
            piece.position = (to_file * self.square_size, to_rank * self.square_size + self.offset)
            piece.has_moved = True