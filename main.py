# Python for COMP30024 Part A

import os

NUM_ROWS = 8
NUM_COLS = 8

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
				newBoard[(rowIndex, colIndex)] = splitInput[rowIndex * NUM_ROWS + colIndex]

		return newBoard, splitInput[-1]


	def printBoard(self):
		'''Prints the board'''
		flatArray = []
		for rowIndex in range(NUM_ROWS):
			for colIndex in range(NUM_COLS):
				print(self.board[(rowIndex, colIndex)], end=' ')

			print('')

	def printBoardType(self):
		'''Prints the type of move'''
		print(self.moveType)


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
# print("Completed!")

os.system("pause")