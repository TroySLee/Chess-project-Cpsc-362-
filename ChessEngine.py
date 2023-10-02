import pygame as p
class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    def getValidMoves(self):
        return self.getAllPossibleMoves()

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if(turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        direction = -1 if self.whiteToMove else 1
        start_row = 6 if self.whiteToMove else 1
        enemy_color = "b" if self.whiteToMove else "w"

        new_r = r + direction
        if 0 <= new_r < 8:
            if self.board[new_r][c] == "--":
                moves.append(Move((r, c), (new_r, c), self.board))
                if r == start_row and self.board[new_r + direction][c] == "--":
                    moves.append(Move((r, c), (new_r + direction, c), self.board))
            for i in [-1, 1]:
                new_c = c + i
                if 0 <= new_c < 8 and self.board[new_r][new_c][0] == enemy_color:
                    moves.append(Move((r, c), (new_r, new_c), self.board))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for i, j in directions:
            for s in range(1, 8):
                end_row, end_col = r + i * s, c + j * s
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    endPiece = self.board[end_row][end_col]
                    if endPiece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        ally_color = "w" if self.whiteToMove else "b"

        for i, j in knight_moves:
            end_row, end_col = r + i, c + j
            if 0 <= end_row < 8 and 0 <= end_col < 8 and self.board[end_row][end_col][0] != ally_color:
                moves.append(Move((r, c), (end_row, end_col), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"

        for i in directions:
            for j in range(1, 8):
                endRow, endCol = r + i[0] * j, c + i[1] * j
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        allyColor = "w" if self.whiteToMove else "b"

        for i, j in kingMoves:
            endRow, endCol = r + i, c + j
            if 0 <= endRow < 8 and 0 <= endCol < 8 and self.board[endRow][endCol][0] != allyColor:
                moves.append(Move((r, c), (endRow, endCol), self.board))

class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + " to " + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

class Button:
    def __init__(self, x, y, image, scale):
        self.image = p.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = p.mouse.get_pos()
        click = p.mouse.get_pressed()[0]

        if self.rect.collidepoint(pos):
            if click and not self.clicked:
                self.clicked = True
                action = True

        if not click:
            self.clicked = False

        surface.blit(self.image, self.rect)

        return action