# HardSudokuSolver
A particularly hard exercise involving the creation of an universal Sudoku solver, taken straight from CodeWars

Problem:
  - Given a 9x9 matrix of integers (from 0 to 9, with 0 representing "unassigned"), provide the completed Sudoku grid (if it exists) or
    an error message in case the input is not valid or the sudoku is not solvable.
    
About my solution:
  - In this solution, I decided to work with a "move stack", to make sure I could undo the effects of any bifurcation that went wrong.
  - Every instance of the SudokuProblem class contains several auxiliary variables:
    - A list of possibilities for every cell (so that if a cell has 1 possibility, it gets assigned that value, and if it has 0, it raises an error)
    - A list containing the number of cells that have a certain possible value for each row, column and box (once again, if there is only 1, assign it,
      and if there is zero, raise an error)
    - The total number of assigned cells (if it reaches 81, the solution is done)
  - One guaranteed invariant within the SudokuProblem class is that, if every input validation method is passed 
    (i.e. checking if the matrix has the right dimensions, the cells have the right values, and no rows/columns/boxes have repeats)
    then a number will never be assigned to a cell if another cell in its row/column/box has that number.
    - Therefore, the only way to spot a logical inconsistency is to check whether a column/row/box has zero possibilities for a number, or if a cell
      has zero potential values. These two checks are made simple by our auxiliary variables.
  - In case no logical steps are found, the program then bifurcates (i.e. tries a possible value for a cell and sees where that goes).
    - This is where the move stack comes into play: if an inconsistency is found, we backtrack along the move stack back to the last bifurcation, to
      attempt different strategies.
  - I intend to add a special place for extra inference rules (say, X-wings and the type) right above the bifurcation lines, but this will take a while
      
Moves in the move stack:
  - Moves in the move stack are in one of two categories:
    - Set moves. Syntax: ("set",row,col,val)
      > When being DONE:
      - Sets the value of row,col to val
      - Increase the number of assigned cells by 1
      - Stacks "rem" instructions for the value in val for every cell in the same row/column/box as row,col
      > When being UNDONE:
      - Sets the value of row,col to 0
      - Lower the number of assigned cells by 1
      - If the move in question is the bifurcation move, then stack a "rem" instruction for row,col,val
  - Remove moves. Syntax: ("rem",row,col,val)
    > When being DONE:
    - Removes val from the possibilities for row,col
      - If only one possible value remains, stack a 'set' instruction for that value
      - If no values remain, raise an "ERROR"
    - Decrease the number of potential cells for val in the row/column/box of row,col by 1
      - If the number of potential cells for val in the row/column/box is 1, then stack a 'set' instruction for the remaining cell
      - If the number of potential cells for val in the row/column/box is 0, raise an "ERROR"
    > When being UNDONE:
    - Adds val to the possibilities for row,col
    - Increase the number of potential cells for val in the row/column/box of row,col by 1
  - There is an extra special instruction consisting only of a string that says "ERROR", which signals that the solver should start
    backtracking to the last bifurcation. I would have used None instead, but I felt it could get confusing.
    - Calls the backtracking method to go to the last bifurcation
      - If no bifurcations exist, raise an Error (as in an actual error) saying the puzzle is unsolvable
