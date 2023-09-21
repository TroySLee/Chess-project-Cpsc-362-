import pygame as p
from Chess import ChessEngine

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = BOARD_WIDTH
MOVE_LOG_PANEL_HEIGHT = 100
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT + MOVE_LOG_PANEL_HEIGHT))
    p.display.set_caption("Chess Game")
    clock = p.time.Clock()
    moveLogFont = p.font.SysFont("Times Roma", 30, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadImages()
    running = True
    menu = True
    sqSelected = ()
    playerClicks = []
    imageLogo = p.image.load("chessLogo.png")
    imageStart = p.image.load("chessStart.png").convert_alpha()
    startButton = ChessEngine.Button(185, 350, imageStart, 1)
    while running:
        if menu:
            screen.fill("dim gray")
            screen.blit(imageLogo, (0, 0))
            if startButton.draw(screen):
                menu = False

            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
            p.display.update()
        else:

            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                        else:
                            playerClicks = [sqSelected]
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_BACKSPACE:
                        gs.undoMove()
                        moveMade = True

            if moveMade:
                validMoves = gs.getValidMoves()
                moveMade = False

            drawGameState(screen, gs, moveLogFont)
            clock.tick(MAX_FPS)
            p.display.flip()


def drawGameState(screen, gs, moveLongFont):
    drawBoard(screen)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLongFont)


def drawBoard(screen):
    colors = [p.Color("light green"), p.Color("light blue")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# This function is completely edited
def drawMoveLog(screen, gs, font):
    logScreen = p.Rect(0, BOARD_HEIGHT, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), logScreen)

    chessLog = gs.moveLog
    moveInfo = [f"{i // 2 + 1}. {chessLog[i].getChessNotation()}  {chessLog[i + 1].getChessNotation()}" if i + 1 < len(
        chessLog) else f"{i // 2 + 1}. {chessLog[i].getChessNotation()}" for i in range(0, len(chessLog), 2)]

    textIndent = 10
    dataRow = 2
    y_axis = textIndent

    for i in range(0, len(moveInfo), dataRow):
        spacing = "  ".join(moveInfo[i:i + dataRow])
        textData = font.render(spacing, True, p.Color("white"))
        textLocation = logScreen.move(textIndent, y_axis)
        screen.blit(textData, textLocation)
        y_axis += textData.get_height()


if __name__ == "__main__":
    main()
