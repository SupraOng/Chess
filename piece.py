import pygame as pg

class Piece:

    none = 0
    pawn = 1
    rook = 2
    knight = 3
    bishop = 4
    queen = 5
    king = 6

    white = 8
    black = 16

    def __init__(self, screen, piece_type, color, position):
        self.screen = screen
        self.piece_type = piece_type
        self.color = color
        self.position = position

        self.has_moved = False
        self.just_moved = False

        self.piece_img = None
        self.piece_imgs = [
            "Pieces/b_rook.png",
            "Pieces/b_knight.png",
            "Pieces/b_bishop.png",
            "Pieces/b_queen.png",
            "Pieces/b_king.png",
            "Pieces/b_pawn.png",
            "Pieces/w_rook.png",
            "Pieces/w_knight.png",
            "Pieces/w_bishop.png",
            "Pieces/w_queen.png",
            "Pieces/w_king.png",
            "Pieces/w_pawn.png"
        ]

    def display_piece(self):
        if self.color == Piece.white:
            match self.piece_type:
                case self.rook:
                    self.piece_img = self.piece_imgs[6]
                case self.knight:
                    self.piece_img = self.piece_imgs[7]
                case self.bishop:
                    self.piece_img = self.piece_imgs[8]
                case self.queen:
                    self.piece_img = self.piece_imgs[9]
                case self.king:
                    self.piece_img = self.piece_imgs[10]
                case self.pawn:
                    self.piece_img = self.piece_imgs[11]
        elif self.color == Piece.black:
            match self.piece_type:
                case self.rook:
                    self.piece_img = self.piece_imgs[0]
                case self.knight:
                    self.piece_img = self.piece_imgs[1]
                case self.bishop:
                    self.piece_img = self.piece_imgs[2]
                case self.queen:
                    self.piece_img = self.piece_imgs[3]
                case self.king:
                    self.piece_img = self.piece_imgs[4]
                case self.pawn:
                    self.piece_img = self.piece_imgs[5]
        
        img = pg.image.load(self.piece_img)
        img = pg.transform.scale(img, (100, 100))
        self.screen.blit(img, (self.position[0], self.position[1]))

