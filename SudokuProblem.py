
class SudokuProblem:

    def __init__(self, puzzle, verbose = True):
        self.puzzle = puzzle.copy()
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
                if element not in range(10):
                    raise ValueError("Sudoku cells must contain numbers from 0 (unassigned) to 9")
    
    def execute_set(self, instruction):
        # do not repeat instruction if it has already been executed
        if self.puzzle[instruction[1]][instruction[2]] == instruction[3]:
            if self.verbose:
                print(f"Set: {instruction[1]},{instruction[2]} is already {instruction[3]}.")
            return []
        elif self.puzzle[instruction[1]][instruction[2]] > 0:
            if self.verbose:
                print(f"Set ERROR: {instruction[1]},{instruction[2]} is already set to {self.puzzle[instruction[1]][instruction[2]]}! ERROR!")
            return ["ERROR"]
        if self.verbose:
            print(f"Setting {instruction[1]},{instruction[2]} to {instruction[3]}.")
        self.puzzle[instruction[1]][instruction[2]] = instruction[3]
        self.assigned += 1
        if not self.check_consistency():
            print("Set ERROR: consistency check failed!")
            return ["ERROR"]
            
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
        
    def set_box(self, box, val):
        # if a hidden single exists, find the corresponding cell
        start_r = 3*(box//3)
        start_c = 3*(box%3)
        for row in range(start_r,start_r+3):
            for col in range(start_c,start_c+3):
                if self.possibilities[row][col][val]:
                    return ("set",row,col,val)
        
    def set_col(self, col, val):
        # if a hidden single exists, find the corresponding cell
        for row in range(9):
            if self.possibilities[row][col][val]:
                return ("set",row,col,val)
        
    def set_row(self, row, val):
        # if a hidden single exists, find the corresponding cell
        for col in range(9):
            if self.possibilities[row][col][val]:
                return ("set",row,col,val)
        
    def execute_rem(self, instruction):
        # prevent re-execution
        if not self.possibilities[instruction[1]][instruction[2]][instruction[3]]:
            if self.verbose:
                print(f"Rem: cell {instruction[1]},{instruction[2]} is already devoid of {instruction[3]} as a possibility!")
            return []
            
        # carry out instructions
        if self.verbose:
            print(f"Removing {instruction[3]} from possibilities for {instruction[1]},{instruction[2]}.")          
        self.possibilities[instruction[1]][instruction[2]][instruction[3]] = False
        self.rows[instruction[1]][instruction[3]] -= 1
        self.cols[instruction[2]][instruction[3]] -= 1
        box = 3*(instruction[1]//3)+(instruction[2]//3)
        self.boxes[box][instruction[3]] -= 1
        
        # CHECK ALL LOGICAL INCONSISTENCIES!
        if sum(self.possibilities[instruction[1]][instruction[2]]) < 2:
            if self.verbose:
                print(f"Rem ERROR: cell {instruction[1]},{instruction[2]} is out of options!")
            return ["ERROR"]
        if self.rows[instruction[1]][instruction[3]] == 0:
            if self.verbose:
                print(f"Rem ERROR: row {instruction[1]} has no place for {instruction[3]}!")
            return ["ERROR"]
        if self.cols[instruction[2]][instruction[3]] == 0:
            if self.verbose:
                print(f"Rem ERROR: column {instruction[2]} has no place for {instruction[3]}!")
            return ["ERROR"]
        if self.boxes[box][instruction[3]] == 0:
            if self.verbose:
                print(f"Rem ERROR: box {box} has no place for {instruction[3]}!")
            return ["ERROR"]
        
        # check for naked single
        instructions_to_add = []
        if sum(self.possibilities[instruction[1]][instruction[2]]) == 2:
            for i in range(1,10):
                if self.possibilities[instruction[1]][instruction[2]][i]:
                    instructions_to_add.append(("set",instruction[1],instruction[2],i))
                    break
        
        # check for hidden single
        if self.rows[instruction[1]][instruction[3]] == 1:
            instructions_to_add.append(self.set_row(instruction[1],instruction[3]))
        if self.cols[instruction[2]][instruction[3]] == 1:
            instructions_to_add.append(self.set_col(instruction[2],instruction[3]))
        if self.boxes[instruction[1]][instruction[3]] == 1:
            instructions_to_add.append(self.set_box(box,instruction[3]))
        
        return instructions_to_add
    
    def execute(self, instruction):
        if instruction[0] == "set":
            return self.execute_set(instruction)
        elif instruction[0] == "rem":
            return self.execute_rem(instruction)
            
    def undo_rem(self, instruction):
        if self.possibilities[instruction[1]][instruction[2]][instruction[3]]:
            if self.verbose:
                print(f"<<< UNDO Rem: cell {instruction[1]},{instruction[2]} already has {instruction[3]} as a possibility!")
            return
        
        # undo rem: remembering to re-increment the possibility variables
        self.possibilities[instruction[1]][instruction[2]][instruction[3]] = True
        self.rows[instruction[1]][instruction[3]] += 1
        self.cols[instruction[2]][instruction[3]] += 1
        box = 3*(instruction[1]//3)+(instruction[2]//3)
        self.boxes[box][instruction[3]] += 1
        
    def undo_set(self, instruction):
        if self.puzzle[instruction[1]][instruction[2]] == 0:
            if self.verbose:
                print(f"<<< UNDO Set: {instruction[1]},{instruction[2]} is already unassigned.")
            return
            
        # undo set: remembering to decrement the assigned variable
        self.puzzle[instruction[1]][instruction[2]] = 0
        self.assigned -= 1
        
    def undo(self, instruction):
        if instruction[0] == "set":
            self.undo_set(instruction)
        elif instruction[0] == "rem":
            self.undo_rem(instruction)
            
    def rewind(self):
        if self.verbose:
            print("<<< REWIND STARTING")
        # backtracks to the last bifurcation
        last_one = self.bifurcations.pop()
        while self.index >= last_one:
            self.undo(self.instructions[index])
            index -= 1
        self.index += 1
        
        # remove the bifurcated possibility, as it led to a
        # contradiction
        bifurc_step = self.instructions[self.index]
        new_command = ("rem",bifurc_step[1],bifurc_step[2],bifurc_step[3])        
        self.instructions = self.instructions[:last_one]
        self.instructions.append(new_command)
        
    def bifurcate(self):
        # chooses a candidate for bifurcation
        # Heuristic used: the most restricted candidate
        cur_candidate = (0,0)
        cur_poss = 11
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] == 0:
                    poss = sum(self.possibilities[i][j])
                    if poss < cur_poss:
                        cur_poss = poss
                        cur_candidate = (i,j)
                        
        for i in range(1,10):
            if self.possibilities[cur_candidate[0]][cur_candidate[1]][i]:
                self.instructions.append(("set",cur_candidate[0],cur_candidate[1],i))
                self.bifurcations.append(len(instructions)-1)
        
    def solve(self):
        # force "set" instructions for givens, to get all deductions
        # possible from them
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] > 0:
                    self.instructions.append(("set",i,j,self.puzzle[i][j]))
                    self.puzzle[i][j] = 0
                    
        # outermost loop: stops when puzzle solved
        while self.assigned < 81:
            # inner loop: stops when no logical deductions are left
            while self.index < len(self.instructions):
                new_commands = self.execute(self.instructions[self.index])
                if new_commands[0] == "ERROR":
                    if len(self.bifurcations) > 0:
                        self.rewind()
                    else:
                        # if an error was raised without any bifurcations,
                        # then the puzzle reached an unsolvable state via
                        # logic deductions alone, implying it is unsolvable
                        raise ValueError("Puzzle is unsolvable! Double check the puzzle if you think that might not be the case.")
                else:
                    self.instructions.extend(new_commands)
                    self.index += 1
            # --- EXTRA INFERENCE RULES GO HERE
            new_inference = False
            # (none so far)
            # ---------------------------------
            # BIFURCATION BELOW
            if not new_inference:
                if self.verbose:
                    print("Out of logical steps. Attempting bifurcation.")
                self.bifurcate()
        if self.verbose:
            for i in range(9):
                print(self.puzzle[i])
        return self.puzzle
        
                    
if __name__ == '__main__':
    pass
