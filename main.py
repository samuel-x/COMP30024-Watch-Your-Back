# Python for COMP30024 Part A

import os

NUM_COLS = 8
NUM_ROWS = 8
BLANK = '-'
CORNER = 'X'
PIECE = ['O', '@']

class Board:
    '''This represents the board in the game world'''

    # Board structure
    board = {}
    # Move Type
    moveType = ''


    def __init__(self, board):
        self.board, self.moveType = self.parseBoard(board)

    def parseBoard(self, boardStr):
        '''Given a string specifying the board layout, converts into a dictionary data structure
        we can more easily use. Also returns the type of operation required.'''
        newBoard = {}
        splitInput = boardStr.split()
        for rowIndex in range(NUM_ROWS):
            for colIndex in range(NUM_COLS):
                newBoard[(colIndex, rowIndex)] = Piece(splitInput[rowIndex * NUM_ROWS + colIndex], 
                    (colIndex, rowIndex))

        return newBoard, splitInput[-1]


    def printBoard(self):
        '''Prints the board'''
        for rowIndex in range(NUM_ROWS):
            for colIndex in range(NUM_COLS):
                print(self.board[(colIndex, rowIndex)], end=' ')

            print('')

    def printBoardType(self):
        '''Prints the type of move'''
        print(self.moveType)

    def getPiece(self, pos):
        return self.board[pos]

    def checkValidMove(self, piece, newPos):
        '''Checks if a move is valid for a specified piece according to the spec.'''
        # Get new coordinates
        newX = newPos[0]
        newY = newPos[1]

        # Check within board bounds
        if (newX >= NUM_COLS or newX < 0 or newY >= NUM_ROWS or newY < 0):
            # print("Move ", newPos, " is out of bounds.")
            return False

        # Get movement from current position
        movementX = newX - piece.getPosX()
        movementY = newY - piece.getPosY()

        # Check if the space is occupied.
        # If it is not, and it is currently one space in the X or Y axis away from the piece, then
        # the move is valid.
        # Otherwise, if the move is two spaces in the X or Y axis away from the piece, then
        # check if there is a piece in between the spaces.
        if (str(self.board[newPos]) == BLANK):
            if ((abs(movementX) == 1) != (abs(movementY) == 1)):
                return True
            elif ((abs(movementX) == 2) and str(self.board[newX - (movementX/2), newY]) in PIECE) !=\
                ((abs(movementY) == 2) and str(self.board[newX, newY - (movementY/2)]) in PIECE):
                return True

        return False

    def getValidMoves(self, piece):
        validMoves = []
        # Check all squares in a 2-square radius around piece
        # could probably optimize this so it only has to check if there's a piece in the middle
        for x in range(-2,3):
            newPos = (piece.getPosX() + x, piece.getPosY())
            if (self.checkValidMove(piece, newPos)):
                validMoves.append(newPos)
        for y in range(-2,3):
            newPos = (piece.getPosX(), piece.getPosY() + y)
            if (self.checkValidMove(piece, newPos)):
                validMoves.append(newPos)

        return validMoves

    def getAllValidMoves(self, pieceType):
        # Updates all pieces with possible moves
        # Also, returns an array containing all pieces on one team
        pieces = []
        for position, piece in self.board.items():
            if (str(piece) == pieceType):
                piece.setValidMoves(self.getValidMoves(piece))
                pieces.append(piece)
        return pieces

    def printAllValidMoves(self, pieceType):
        pieces = self.getAllValidMoves(pieceType)
        for piece in pieces:
            currentPos = piece.getPos()
            for newPos in piece.getValidMoves():
                print(currentPos, "->", newPos)



class Piece:
    '''This represents a piece in the game world.
    A piece is either a O or a @. If it is a X or a - it is considered a corner or a blank space
    respectively'''
    def __init__(self, team, pos, validMoves=[]):
        self.team = team
        self.pos = pos
        self.validMoves = validMoves

    def __str__(self):
        return self.team

    def setValidMoves(self, validMoves):
        self.validMoves = validMoves

    def getValidMoves(self):
        return self.validMoves

    def getPos(self):
        return self.pos

    def getPosX(self):
        return self.pos[0]

    def getPosY(self):
        return self.pos[1]


# Testing 
boardStr = """
X - - - O O - X
- - - O - O O -
O - O - - - - @
- - - O O O - @
O O O - - @ @ -
- @ @ - @ @ @ -
- @ @ @ - - - -
X - - - - - - X
Moves
"""
board = Board(boardStr)
board.printBoard()
board.printBoardType()

# piece = board.getPiece((5, 1))
# print("down 1 space", board.checkValidMove(piece, (5, 2)))
# print("left 1 space", board.checkValidMove(piece, (4, 1)))
# print("diag", board.checkValidMove(piece, (4, 2)))
# print("right 2 spaces", board.checkValidMove(piece, (7, 1)))
# print(board.getValidMoves(piece))
print("Printing all possible moves for \'O\' pieces...")
print(board.printAllValidMoves("O"))
print("Completed!")


os.system("pause")