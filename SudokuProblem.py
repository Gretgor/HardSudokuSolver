
class SudokuProblem:
    """
    Class contains Sudoku problem, and the solver for said problem
    """

    def __init__(self, puzzle, verbose = True):
        # puzzle: initial grid state
        self.puzzle = puzzle.copy()
        
        # number of assigned grid elements
        self.assigned = 0
        
        # possibility arrays to easily spot naked and hidden singles
        self.possibilities = [[[True for _ in range(10)] for _ in range(9)] for _ in range(9)]
        self.rows = [[9 for _ in range(10)] for _ in range(9)]
        self.cols = [[9 for _ in range(10)] for _ in range(9)]
        self.boxes = [[9 for _ in range(10)] for _ in range(9)]
        
        # instruction set, keeping track of bifurcations, etc
        self.instructions = []
        self.index = 0
        self.bifurcations = []
        
        # set verbose if you want to accompany the logical steps taken
        self.verbose = verbose
        
        # validates input
        self.validate_input()
        
        # validates consistency
        if not self.check_consistency():
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
        """
        Executes a 'set' function, which sets a specific cell of the
        grid to a value. Also updates the assigned counter.
        - Returns a list of 'rem' instructions corresponding to elements
          in the same row/box/column as the set cell for the cell's
          new value, as well as the set cell for values different from
          its new value
        """
        # do not repeat instruction if it has already been executed
        if self.puzzle[instruction[1]][instruction[2]] == instruction[3]:
            return []
            
        # if the cell is already set to something else, then an 
        # inconsistency occurred at some point in the execution
        elif self.puzzle[instruction[1]][instruction[2]] > 0:
            if self.verbose:
                print(f"Set ERROR: {instruction[1]},{instruction[2]} is already set to {self.puzzle[instruction[1]][instruction[2]]}! Can't set it to {instruction[3]}!")
            # must reduce index by 1 so move does not get undone
            self.index -= 1
            return ["ERROR"]
        if self.verbose:
            print(f"Setting {instruction[1]},{instruction[2]} to {instruction[3]}.")
        self.puzzle[instruction[1]][instruction[2]] = instruction[3]
        self.assigned += 1
            
        stack_to_add = []
        
        # REM instructions: for self
        for v in range(1,10):
            if v != instruction[3]:
                if self.possibilities[instruction[1]][instruction[2]][v]:
                    stack_to_add.append(("rem",instruction[1],instruction[2],v))
        
        # REM instructions: for row
        i = instruction[1]
        for j in range(0,9):
            if j != instruction[2]:
                if self.possibilities[i][j][instruction[3]]:
                    stack_to_add.append(("rem",i,j,instruction[3]))
        
        # REM instruction: for column
        j = instruction[2]
        for i in range(0,9):
            if i != instruction[1]:
                if self.possibilities[i][j][instruction[3]]:
                    stack_to_add.append(("rem",i,j,instruction[3]))
        
        # REM instruction: for box
        start_r = 3*(instruction[1]//3)
        start_c = 3*(instruction[2]//3)
        for i in range(start_r, start_r+3):
            for j in range(start_c, start_c+3):
                if i != instruction[1] or j != instruction[2]:
                    if self.possibilities[i][j][instruction[3]]:
                        stack_to_add.append(("rem",i,j,instruction[3]))
        
        return stack_to_add 
        
    def set_box(self, box, val):
        """
        given a box with only one cell that can take a certain 
        value, return a 'set' instruction for that cell and that value,
        unless said cell either already has that value (None), or has a
        different value (ERROR)
        """
        # if a hidden single exists, find the corresponding cell
        start_r = 3*(box//3)
        start_c = 3*(box%3)
        for row in range(start_r,start_r+3):
            for col in range(start_c,start_c+3):
                if self.possibilities[row][col][val]:
                    if self.puzzle[row][col] == val:
                        return None
                    if self.puzzle[row][col] > 0:
                        return "ERROR"
                    if self.verbose:
                        print(f"Hidden single found! Cell {row},{col} only cell in box for {val}")
                    return ("set",row,col,val)
        
    def set_col(self, col, val):
        """
        given a column with only one cell that can take a certain 
        value, return a 'set' instruction for that cell and that value,
        unless said cell either already has that value (None), or has a
        different value (ERROR)
        """
        # if a hidden single exists, find the corresponding cell
        for row in range(9):
            if self.possibilities[row][col][val]:
                if self.puzzle[row][col] == val:
                    return None
                if self.puzzle[row][col] > 0:
                    return "ERROR"
                if self.verbose:
                    print(f"Hidden single found! Cell {row},{col} only cell in column for {val}")
                return ("set",row,col,val)
        
    def set_row(self, row, val):
        """
        given a row with only one cell that can take a certain 
        value, return a 'set' instruction for that cell and that value,
        unless said cell either already has that value (None), or has a
        different value (ERROR)
        """
        # if a hidden single exists, find the corresponding cell
        for col in range(9):
            if self.possibilities[row][col][val]:
                if self.puzzle[row][col] == val:
                    return None
                if self.puzzle[row][col] > 0:
                    return "ERROR"
                if self.verbose:
                    print(f"Hidden single found! Cell {row},{col} only cell in row for {val}")
                return ("set",row,col,val)
        
    def execute_rem(self, instruction):
        """
        remove a value from the list of possibiliites of a cell.
        also updates the possibility arrays for the cell's 
        row/column/box
        """
        # prevent re-execution
        if not self.possibilities[instruction[1]][instruction[2]][instruction[3]]:
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
        
        return []
        
    def check_singles(self):
        """
        Checks for naked and hidden singles in the grid.
        Returns 'set' instructions for found singles.
        """
        instructions_to_add = []
        # check for naked single
        for i in range(9):
            for j in range(9):
                if sum(self.possibilities[i][j]) == 2 and self.puzzle[i][j] < 1:
                    k = [a for a in range(1,10) if self.possibilities[i][j][a]][0]
                    instructions_to_add.append(("set",i,j,k))
        
        # check for hidden single
        for row in range(9):
            for value in range(1,10):
                if self.rows[row][value] == 1:
                    inst = self.set_row(row,value)
                    if inst is not None:
                        if inst == "ERROR":
                            return ["ERROR"]
                        else:
                            instructions_to_add.append(inst)
        for col in range(9):
            for value in range(1,10):
                if self.cols[col][value] == 1:
                    inst = self.set_col(col,value)
                    if inst is not None:
                        if inst == "ERROR":
                            return ["ERROR"]
                        else:
                            instructions_to_add.append(inst)
        for box in range(9):
            for value in range(1,10):
                if self.boxes[box][value] == 1:
                    inst = self.set_box(box,value)
                    if inst is not None:
                        if inst == "ERROR":
                            return ["ERROR"]
                        else:
                            instructions_to_add.append(inst)
        return instructions_to_add
    
    def execute(self, instruction):
        """
        checks whether instruction is 'set' or 'rem' to call the correct
        execution method
        """
        if instruction[0] == "set":
            return self.execute_set(instruction)
        elif instruction[0] == "rem":
            return self.execute_rem(instruction)
            
    def undo_rem(self, instruction):
        """
        undoes the effects of a 'rem' instruction
        """
        if self.possibilities[instruction[1]][instruction[2]][instruction[3]]:
            return
        
        # undo rem: remembering to re-increment the possibility variables
        self.possibilities[instruction[1]][instruction[2]][instruction[3]] = True
        self.rows[instruction[1]][instruction[3]] += 1
        self.cols[instruction[2]][instruction[3]] += 1
        box = 3*(instruction[1]//3)+(instruction[2]//3)
        self.boxes[box][instruction[3]] += 1
        
    def undo_set(self, instruction):
        """
        undoes the effects of a 'set' instruction
        """
        if self.puzzle[instruction[1]][instruction[2]] == 0:
            return
            
        # undo set: remembering to decrement the assigned variable
        self.puzzle[instruction[1]][instruction[2]] = 0
        self.assigned -= 1
        
    def undo(self, instruction):
        """
        checks whether instruction is 'set' or 'rem' to call the correct
        undoing method
        """
        if self.verbose:
            print(f"Undoing type {instruction[0]}, cell {instruction[1]},{instruction[2]}, value {instruction[3]}")
        if instruction[0] == "set":
            self.undo_set(instruction)
        elif instruction[0] == "rem":
            self.undo_rem(instruction)
            
    def rewind(self):
        """
        rewinds the puzzle's state back to the latest bifurcation, by
        undoing all instructions done after said bifurcation.
        
        also stacks a 'rem' instruction for the value attempted in the
        bifurcation, so the algorithm can try something else
        """
        if self.index >= len(self.instructions):
            self.index = len(self.instructions) - 1
        if self.verbose:
            print("<<< REWIND STARTING")
        # backtracks to the last bifurcation
        last_one = self.bifurcations.pop()
        while self.index >= last_one:
            self.undo(self.instructions[self.index])
            self.index -= 1
        self.index += 1
        
        # remove the bifurcated possibility, as it led to a
        # contradiction (or to test another potential solution)
        bifurc_step = self.instructions[self.index]
        new_command = ("rem",bifurc_step[1],bifurc_step[2],bifurc_step[3])        
        self.instructions = self.instructions[:last_one]
        self.instructions.append(new_command)
        
    def bifurcate(self):
        """
        selects an unset cell with the minimum amount of possibilities,
        stacks a 'set' instruction for its lowest possible value, and
        marks it as a bifurcation (to be undone later by a rewind)
        """
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
                self.bifurcations.append(len(self.instructions)-1)
                break
        
    def solve(self):
        """
        main solver algorithm. Attempts to complete the grid contained 
        in self.puzzle. Returns the complete grid if a solution exists
        and is unique, and otherwise raises errors.
        """
        solution = [[0 for _ in range(9)] for _ in range(9)]
        # force "set" instructions for givens, to get all deductions
        # possible from them
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] > 0:
                    self.instructions.append(("set",i,j,self.puzzle[i][j]))
                    self.puzzle[i][j] = 0
                    
        stop = False
        solutions = 0
        # outermost loop: stops when puzzle is solved or impossible
        while stop == False:
            # inner loop: stops when no logical deductions are left
            while self.index < len(self.instructions):
                if self.instructions[self.index] != "ERROR":
                    new_commands = self.execute(self.instructions[self.index])
                else:
                    new_commands = [self.instructions.pop()]
                if new_commands and new_commands[0] == "ERROR":
                    if len(self.bifurcations) > 0:
                        self.rewind()
                    else:
                        # if an error was raised without any bifurcations,
                        # then the puzzle reached an unsolvable state via
                        # logic deductions alone, implying it is unsolvable
                        # (or the removal of previously valid solutions
                        # made it unsolvable)
                        stop = True
                        break
                else:
                    self.instructions.extend(new_commands)
                    self.index += 1
            solution_found = False
            if self.assigned == 81:
                # if all 81 cells are assigned, a solution was found.
                # given that no repeats are ever placed into the grid
                # by the solution algorithm, then we know this solution
                # to be consistent
                if self.verbose:
                    print("SOLUTION FOUND!")
                    for i in range(9):
                        print(self.puzzle[i])
                    print("--------")
                solution_found = True
                solutions += 1
                if solutions >= 2:
                    raise ValueError("Puzzle has multiple solutions!")
                # if this is the first solution found, register it
                for i in range(9):
                    for j in range(9):
                        solution[i][j] = self.puzzle[i][j]
                # if this solution was found without bifurcations,
                # then the puzzle is uniquely solvable
                if len(self.bifurcations) == 0:
                    if self.verbose:
                        for i in range(9):
                            print(self.puzzle[i])
                    return solution
                else:
                    self.rewind()
            else:
                # no more instructions: check for naked and hidden 
                # singles. 
                more_instructions = self.check_singles()
                self.instructions.extend(more_instructions)
                # --- EXTRA INFERENCE RULES GO HERE
                # (none so far)
                # ---------------------------------
                
            # BIFURCATION BELOW
            # (the instruction pointer has run out of instructions, no
            # new naked/hidden singles were found, and no new solution
            # was found)
            if len(self.instructions) <= self.index and not solution_found:
                if self.verbose:
                    print("Out of logical steps. Attempting bifurcation.")
                self.bifurcate()
        if solutions == 0:
            raise ValueError("Puzzle is unsolvable")
        return solution
        
                    
if __name__ == '__main__':
    puzzle = [
          [6, 1, 8, 0, 0, 0, 3, 4, 2],
[0, 0, 3, 6, 0, 1, 7, 0, 0],
[0, 7, 0, 0, 4, 0, 0, 1, 0],
[0, 5, 0, 9, 0, 4, 0, 3, 0],
[0, 0, 9, 0, 0, 0, 1, 0, 0],
[1, 6, 4, 7, 0, 8, 0, 2, 0],
[0, 3, 0, 0, 6, 0, 0, 8, 7],
[0, 2, 5, 3, 0, 9, 4, 0, 1],
[7, 0, 0, 0, 0, 2, 0, 0, 3]
        ]
    problem = SudokuProblem(puzzle)
    if not problem.check_consistency():
        raise ValueError("Final result is invalid")
    solution = problem.solve()
    print("Concluded")
