
class SudokuProblem:

    def __init__(self, puzzle, verbose = True):
        self.puzzle = puzzle
        self.assigned = 0
        self.possibilities = [[[True for _ in range(10)] for _ in range(9)] for _ in range(9)]
        self.rows = [[9 for _ in range(10)] for _ in range(9)]
        self.cols = [[9 for _ in range(10)] for _ in range(9)]
        self.boxes = [[9 for _ in range(10)] for _ in range(9)]
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
    
    def execute_set(instruction):
        # do not repeat instruction if it has already been executed
        if puzzle[instruction[1]][instruction[2]] == instruction[3]:
            if self.verbose:
                print(f"Set: {instruction[1]},{instruction[2]} is already {instruction[3]}."
            return []
        elif puzzle[instruction[1]][instruction[2]] > 0:
            if self.verbose:
                print(f"Set ERROR: {instruction[1]},{instruction[2]} is already set to {puzzle[instruction[1]][instruction[2]]}! ERROR!"
            return ["ERROR"]
        if self.verbose:
            print(f"Setting {instruction[1]},{instruction[2]} to {instruction[3]}."
        puzzle[instruction[1]][instruction[2]] = instruction[3]
        self.assigned += 1
        stack_to_add = []
        
        # REM instructions: for self
        for v in range(1,10):
            if v != instruction[3]:
                stack_to_add.append(("rem",instruction[1],instruction[2],v))
        
        # REM instructions: for row
        i = instruction[1]
        for j in range(0,9):
            if j != instruction[2]:
                stack_to_add.append(("rem",i,j,instruction[3]))
        
        # REM instruction: for column
        j = instruction[2]
        for i in range(0,9):
            if i != instruction[1]:
                stack_to_add.append(("rem",i,j,instruction[3]))
        
        # REM instruction: for box
        start_r = 3*(instruction[1]//3)
        start_c = 3*(instruction[2]//3)
        for i in range(start_r, start_r+3):
            for j in range(start_c, start_c+3):
                if i != instruction[1] or j != instruction[2]:
                    stack_to_add.append(("rem",i,j,instruction[3]))
        
        return stack_to_add 
        
    def set_box(box, val):
        pass
        
    def set_col(col, val):
        pass
        
    def set_row(row, val):
        pass
        
    def execute_rem(instruction):
        # prevent re-execution
        if not possibilities[instruction[1]][instruction[2]][instruction[3]]:
            if self.verbose:
                print(f"Rem: cell {instruction[1]},{instruction[2]} is already devoid of {instruction[3]} as a possibility!")
            return []
            
        # carry out instructions
        if self.verbose:
            print(f"Removing {instruction[3]} from possibilities for {instruction[1]},{instruction[2]}."            
        possibilities[instruction[1]][instruction[2]][instruction[3]] = False
        rows[instruction[1]][instruction[3]] -= 1
        cols[instruction[2]][instruction[3]] -= 1
        box = 3*(instruction[1]//3)+(instruction[2]//3)
        boxes[box][instruction[3]] -= 1
        
        # CHECK ALL LOGICAL INCONSISTENCIES!
        if sum(possibilities[instruction[1]][instruction[2]]) < 2:
            if self.verbose:
                print(f"Rem ERROR: cell {instruction[1]},{instruction[2]} is out of options!")
            return ["ERROR"]
        if rows[instruction[1]][instruction[3]] == 0:
            if self.verbose:
                print(f"Rem ERROR: row {instruction[1]} has no place for {instruction[3]}!")
            return ["ERROR"]
        if cols[instruction[2]][instruction[3]] == 0:
            if self.verbose:
                print(f"Rem ERROR: column {instruction[2]} has no place for {instruction[3]}!")
            return ["ERROR"]
        if boxes[box][instruction[3]] == 0:
            if self.verbose:
                print(f"Rem ERROR: box {box} has no place for {instruction[3]}!")
            return ["ERROR"]
        
    
    def execute(instruction):
        if instruction[0] == "set":
            execute_set(instruction)
        elif instruction[0] == "rem":
            execute_rem(instruction)
                    
    


if __name__ == '__main__':
    pass
