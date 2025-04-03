import pygame 
import sys
import random
import time
from typing import List, Tuple, Optional

# Initialize pygame
pygame.init()

# Constants
WINDOW_SIZE = 540
GRID_SIZE = 9
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 128, 0)

class SudokuGame:
    """
    Sudoku Game Class implementing core functionality and visualization
    """
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 50))
        pygame.display.set_caption("Sudoku")
        self.font = pygame.font.SysFont('Arial', 32)
        self.small_font = pygame.font.SysFont('Arial', 20)
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.solution = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.original = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected = None
        self.difficulty = "medium"  # easy, medium, hard
        self.message = ""
        self.message_time = 0
        self.generate_puzzle()
    
    def generate_puzzle(self) -> None:
        """Generate a new Sudoku puzzle based on difficulty"""
        # Generate a complete solution
        self.generate_solution()
        
        # Create a puzzle by removing numbers
        cells_to_remove = {
            "easy": 40,
            "medium": 50,
            "hard": 60
        }.get(self.difficulty, 50)
        
        # Copy solution to board
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.board[i][j] = self.solution[i][j]
                self.original[i][j] = True
        
        # Remove cells while ensuring unique solution
        removed = 0
        attempts = 0
        while removed < cells_to_remove and attempts < 200:
            row, col = random.randint(0, 8), random.randint(0, 8)
            if self.board[row][col] != 0:
                backup = self.board[row][col]
                self.board[row][col] = 0
                self.original[row][col] = False
                
                # Check for unique solution
                temp_board = [row[:] for row in self.board]
                if self.count_solutions(temp_board) == 1:
                    removed += 1
                else:
                    self.board[row][col] = backup
                    self.original[row][col] = True
                attempts += 1
    
    def generate_solution(self) -> bool:
        """Generate a complete Sudoku solution using backtracking"""
        # Start with empty board
        self.solution = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Fill diagonal boxes first (independent of each other)
        for box in range(0, GRID_SIZE, 3):
            self.fill_box(box, box)
        
        # Solve the rest of the board
        return self.solve_sudoku(self.solution)
    
    def fill_box(self, row: int, col: int) -> None:
        """Fill a 3x3 box with random numbers"""
        nums = list(range(1, 10))
        random.shuffle(nums)
        index = 0
        for i in range(3):
            for j in range(3):
                self.solution[row + i][col + j] = nums[index]
                index += 1
    
    def solve_sudoku(self, board: List[List[int]]) -> bool:
        """Solve Sudoku using backtracking algorithm"""
        empty = self.find_empty_cell(board)
        if not empty:
            return True
        
        row, col = empty
        
        for num in range(1, 10):
            if self.is_valid(board, row, col, num):
                board[row][col] = num
                
                if self.solve_sudoku(board):
                    return True
                
                board[row][col] = 0
        
        return False
    
    def count_solutions(self, board: List[List[int]], count: int = 0) -> int:
        """Count number of solutions to ensure puzzle uniqueness"""
        empty = self.find_empty_cell(board)
        if not empty:
            return count + 1
        
        row, col = empty
        
        for num in range(1, 10):
            if count >= 2:
                return count
            
            if self.is_valid(board, row, col, num):
                board[row][col] = num
                count = self.count_solutions(board, count)
                board[row][col] = 0
        
        return count
    
    def find_empty_cell(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """Find next empty cell (with 0)"""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    def is_valid(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if a number can be placed in a cell"""
        # Check row
        for j in range(GRID_SIZE):
            if board[row][j] == num:
                return False
        
        # Check column
        for i in range(GRID_SIZE):
            if board[i][col] == num:
                return False
        
        # Check 3x3 box
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        
        for i in range(3):
            for j in range(3):
                if board[box_row + i][box_col + j] == num:
                    return False
        
        return True
    
    def draw(self) -> None:
        """Draw the Sudoku board and UI"""
        self.screen.fill(WHITE)
        
        # Draw grid lines
        for i in range(GRID_SIZE + 1):
            # Thicker lines for 3x3 boxes
            line_width = 3 if i % 3 == 0 else 1
            pygame.draw.line(
                self.screen, BLACK, 
                (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE), line_width
            )
            pygame.draw.line(
                self.screen, BLACK, 
                (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE), line_width
            )
        
        # Draw numbers
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.board[i][j] != 0:
                    color = BLACK if self.original[i][j] else LIGHT_BLUE
                    text = self.font.render(str(self.board[i][j]), True, color)
                    self.screen.blit(
                        text, 
                        (j * CELL_SIZE + CELL_SIZE // 3, i * CELL_SIZE + CELL_SIZE // 6)
                    )
        
        # Draw selected cell
        if self.selected:
            i, j = self.selected
            pygame.draw.rect(
                self.screen, GREEN,
                (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3
            )
        
        # Draw difficulty buttons
        difficulties = ["easy", "medium", "hard"]
        for idx, diff in enumerate(difficulties):
            color = GREEN if self.difficulty == diff else GRAY
            pygame.draw.rect (
                self.screen, color,
                (idx * 180, WINDOW_SIZE, 180, 50))
            text = self.small_font.render(diff.capitalize(), True, BLACK)
            self.screen.blit(text, (idx * 180 + 60, WINDOW_SIZE + 15))
        
        # Draw message
        if self.message and time.time() - self.message_time < 3:
            text = self.small_font.render(self.message, True, RED)
            self.screen.blit(text, (10, WINDOW_SIZE + 10))
    
    def set_message(self, msg: str) -> None:
        """Display a temporary message"""
        self.message = msg
        self.message_time = time.time()
    
    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse clicks"""
        x, y = pos
        
        # Check difficulty buttons
        if y >= WINDOW_SIZE:
            if x < 180:
                self.difficulty = "easy"
            elif x < 360:
                self.difficulty = "medium"
            else:
                self.difficulty = "hard"
            self.generate_puzzle()
            return
        
        # Select cell
        row, col = y // CELL_SIZE, x // CELL_SIZE
        if not self.original[row][col]:
            self.selected = (row, col)
    
    def handle_key(self, key: int) -> None:
        """Handle keyboard input"""
        if not self.selected:
            return
        
        row, col = self.selected
        
        if key == pygame.K_RETURN:
            # Check solution
            if self.check_solution():
                self.set_message("Correct solution!")
            else:
                self.set_message("Some errors found!")
        elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE:
            self.board[row][col] = 0
        elif pygame.K_1 <= key <= pygame.K_9:
            num = key - pygame.K_0
            if not self.original[row][col]:
                self.board[row][col] = num
        elif key == pygame.K_UP and row > 0:
            self.selected = (row - 1, col)
        elif key == pygame.K_DOWN and row < 8:
            self.selected = (row + 1, col)
        elif key == pygame.K_LEFT and col > 0:
            self.selected = (row, col - 1)
        elif key == pygame.K_RIGHT and col < 8:
            self.selected = (row, col + 1)
    
    def check_solution(self) -> bool:
        """Check if current board matches solution"""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.board[i][j] != self.solution[i][j]:
                    return False
        return True
    
    def solve_puzzle(self) -> None:
        """Show the solution"""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if not self.original[i][j]:
                    self.board[i][j] = self.solution[i][j]
        self.set_message("Solution displayed")
    
    def clear_board(self) -> None:
        """Clear user inputs"""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if not self.original[i][j]:
                    self.board[i][j] = 0
        self.set_message("Board cleared")

def main():
    game = SudokuGame()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event.key)
        
        game.draw()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()