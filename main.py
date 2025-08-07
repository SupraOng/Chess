import pygame as pg
from board import Board
from piece import Piece

class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((1200, 900))
        pg.display.set_caption("Chess")

        self.clock = pg.time.Clock()
        self.running = True

        self.board = Board(self.screen)
        
    
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
            
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.board.handle_click(event.pos[0], event.pos[1])
            
            # Handles promotion logic
            if self.board.promoting:
                piece_type = None
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_1:
                        piece_type = Piece.queen
                    elif event.key == pg.K_2:
                        piece_type = Piece.bishop
                    elif event.key == pg.K_3:
                        piece_type = Piece.knight
                    elif event.key == pg.K_4:
                        piece_type = Piece.rook
                    else:
                        continue

                    file, rank = self.board.promotion_square
                    color = self.board.promotion_color
                    self.board.board[file][rank] = Piece(self.board.screen, piece_type, color, 
                                                         (file * self.board.square_size, rank * self.board.square_size))
                    self.board.promoting = False
                    self.board.promotion_square = None
                    self.board.promotion_color = None
                    self.board.switch_turns()

    def run(self):
        while self.running:
            self.handle_events()

            self.screen.fill((0, 0, 0))

            # Update board
            self.board.draw()

            pg.display.flip()
            self.clock.tick(60)

        pg.quit()

if __name__ == "__main__":
    game = Game()
    game.run()