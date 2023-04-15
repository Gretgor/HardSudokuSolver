
class SudokuProblem:

    def __init__(self, puzzle, verbose = True):
        self.puzzle = puzzle
        self.assigned = 0
        self.possibilities = [[[True for _ in range(10)] for _ in range(9)] for _ in range(9)]
        self.rows = [[[9 for _ in range(10)] for _ in range(9)] for _ in range(9)]
        self.cols = [[[9 for _ in range(10)] for _ in range(9)] for _ in range(9)]
        self.boxes = [[[9 for _ in range(10)] for _ in range(9)] for _ in range(9)]
        self.instructions = []
        self.index = 0
        self.bifurcations = []
        self.verbose = verbose
        validate_input()
        if not check_consistency():
            raise ValueError("Input grid contains repeats")
        
    def check_consistency(self):
        """
        Checks if there exist repeats in the puzzle (i.e. repeated 
        values in rows/columns/boxes).
        Returns True if the puzzle is repeat-free, and False otherwise
        """
        puzzle = self.puzzle
        for i in range (0,9):
            # check for rows
            amount = [0,0,0,0,0,0,0,0,0,0]
            for j in range(0,9):
                amount[puzzle[i][j]] += 1
                if puzzle[i][j] > 0 and amount[puzzle[i][j]] > 1:
                    return False
            # check for columns
            amount = [0,0,0,0,0,0,0,0,0,0]
            for j in range(0,9):
                amount[puzzle[j][i]] += 1
                if puzzle[j][i] > 0 and amount[puzzle[j][i]] > 1:
                    return False
            # check for boxes
            amount = [0,0,0,0,0,0,0,0,0,0]
            first_col = (i%3)*3
            first_row = (i//3)*3
            for r in range(first_row, first_row+3):
                for c in range(first_col, first_col+3):
                    amount[puzzle[r][c]] += 1
                    if puzzle[r][c] > 0 and amount[puzzle[r][c]] > 1:
                        return False
        return True

    def validate_input(self):
        """
        Checks if the input is a valid sudoku grid:
        - checks if the puzzle is a 9x9 grid
        - checks if every entry is an integer in range(10)
        Returns an error if an inconsistency is found
        """
        if len(self.puzzle) != 9:
            raise TypeError("Sudoku grid must be 9x9")
        for row in self.puzzle:
            if len(row) != 9:
                raise TypeError("Sudoku grid must be 9x9")
            for element in row:
                if element not in range(0,10):
                    raise ValueError("Sudoku cells must contain numbers from 0 (unassigned) to 9")
                    
    


if __name__ == '__main__':
    pass
