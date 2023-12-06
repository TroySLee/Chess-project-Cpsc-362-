import pygame as p
from Chess import ChessEngine

p.font.init()
BOARD_WIDTH = BOARD_HEIGHT = PANEL_HEIGHT = 550
LEFT_PANEL_WIDTH = RIGHT_PANEL_WIDTH = 200
white_timer = black_timer = 600
MOVE_LOG_PANEL_WIDTH = BOARD_WIDTH
MOVE_LOG_PANEL_HEIGHT = 100
DIMENSION = 8
last_time = p.time.get_ticks()
SQ_SIZE = 480 // DIMENSION
playing_game = False
game_over_sound_played = False
MAX_FPS = 15
IMAGES = {}
captured_pieces = {'w': [], 'b': []}
captured_font = p.font.SysFont("Free Sans Bold", 18, False, False)

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    global white_timer, black_timer, last_time, playing_game

    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + LEFT_PANEL_WIDTH + RIGHT_PANEL_WIDTH, BOARD_HEIGHT + MOVE_LOG_PANEL_HEIGHT))
    p.display.set_caption("Chess Game")
    clock = p.time.Clock()
    moveLogFont = p.font.SysFont("Free Sans Bold", 24, False, False)
    timersFont = p.font.SysFont("Free Sans Bold", 27, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    text = ""
    playing_game = False
    moveMade = False
    sounds = False
    running = True
    menu = True
    gameOver = False
    gameTime = 1000.0
    loadImages()
    sqSelected = ()
    playerClicks = []
    imageLogo = p.image.load("chessLogo.png")
    imageStart = p.image.load("chessStart.png").convert_alpha()
    startButton = ChessEngine.Button(384, 350, imageStart, 1)
    restartImage = p.image.load("Restart.png").convert_alpha()
    restartButton = ChessEngine.Button(320, 270, restartImage, 1)
    quitImage = p.image.load("Quit.png").convert_alpha()
    quitButton = ChessEngine.Button(325, 400, quitImage, 1)

    while running:
        if menu:
            screen.fill("dim gray")
            screen.blit(imageLogo, (198, 0))
            if startButton.draw(screen):
                menu = False
                playing_game = True
                last_time = p.time.get_ticks()
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
            p.display.update()
        else:
            board_start_x = (screen.get_width() - 400) // 15
            board_start_y = (screen.get_height() - 480) // 5
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    if not gameOver:
                        location = p.mouse.get_pos()
                        col = (location[0] - LEFT_PANEL_WIDTH - board_start_x) // SQ_SIZE
                        row = (location[1] - board_start_y) // SQ_SIZE
                        if restartButton is not None and restartButton.clicked:
                            gs = ChessEngine.GameState()
                            validMoves = gs.getValidMoves()
                            gameOver = False
                            playing_game = True
                            restartButton = None
                        if 0 <= row < DIMENSION and 0 <= col < DIMENSION:
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
                                    sounds = True
                                    sqSelected = ()
                                    playerClicks = []
                                else:
                                    playerClicks = [sqSelected]
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_BACKSPACE:
                        if not gameOver:
                            if len(gs.moveLog) > 0:
                                last_move = gs.moveLog[-1]
                                gs.undoMove()
                                moveMade = True
                                sounds = False
                                updateCapturedPiecesOnUndo(last_move)
            if playing_game:
                current_time = p.time.get_ticks()
                elapsed_time = (current_time - last_time) / gameTime
                if gs.checkMate or gs.staleMate:
                    gameOver = True
                    if gs.staleMate:
                        text = "Stalemate"
                        winnerSoundEffect()
                    else:
                        text = "Black Wins Checkmate" if gs.whiteToMove else "White Wins Checkmate"
                    drawEndGameText(screen, text)
                    winnerSoundEffect()
                    playing_game = False
                else:
                    if gs.whiteToMove:
                        white_timer -= elapsed_time
                        white_timer = max(white_timer, 0)
                        if white_timer == 0:
                            gameOver = True
                            text = "Black Wins By Time"
                            playing_game = False
                            timerSoundEffect()
                    else:
                        black_timer -= elapsed_time
                        black_timer = max(black_timer, 0)
                        if black_timer == 0:
                            gameOver = True
                            text = "White Wins By Time"
                            playing_game = False
                            timerSoundEffect()
                last_time = current_time

                if moveMade:
                    if sounds:
                        soundEffects(gs.moveLog[-1])
                    validMoves = gs.getValidMoves()
                    moveMade = False
                    sounds = False

            drawGameState(screen, gs, moveLogFont, validMoves, sqSelected)
            drawTimers(screen, timersFont)
            drawCapturedPieces(screen)
            if gameOver:
                drawEndGameText(screen, text)
                if restartButton.draw(screen):
                    p.mixer.music.stop()
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()

                    gameOver = False
                    playing_game = True
                    white_timer = 602
                    black_timer = 600
                    captured_pieces['w'] = []
                    captured_pieces['b'] = []
                if quitButton.draw(screen):
                    running = False

            restartButton = ChessEngine.Button(320, 270, restartImage, 1)
            quitButton = ChessEngine.Button(325, 400, quitImage, 1)
            clock.tick(MAX_FPS)
            p.display.flip()
            p.display.update()

def drawGameState(screen, gs, moveLongFont, validMoves, sqSelected):
    board_start_x = (screen.get_width() - 400) // 15
    board_start_y = (screen.get_height() - 480) // 5

    drawBoard(screen, LEFT_PANEL_WIDTH, board_start_x, board_start_y)
    drawPieces(screen, gs.board, LEFT_PANEL_WIDTH, board_start_x, board_start_y)

    left_side_rect = p.Rect(0, 0, LEFT_PANEL_WIDTH, PANEL_HEIGHT)
    right_side_rect = p.Rect(BOARD_WIDTH + LEFT_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, PANEL_HEIGHT)

    p.draw.rect(screen, p.Color("gray"), left_side_rect)
    p.draw.rect(screen, p.Color("gray"), right_side_rect)

    drawBoard(screen, left_side_rect.width, board_start_x, board_start_y)
    drawPieces(screen, gs.board, left_side_rect.width, board_start_x, board_start_y)

    drawMoveLog(screen, gs, moveLongFont)

    highlightSquares(screen, gs, validMoves, sqSelected)

def drawBoard(screen, left_width, board_start_x, board_start_y):
    panel_rect = p.Rect(left_width, 0, BOARD_WIDTH, BOARD_HEIGHT)
    p.draw.rect(screen, p.Color("light yellow"), panel_rect)
    colors = [p.Color("light green"), p.Color("light blue")]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color,
                        p.Rect(c * SQ_SIZE + left_width + board_start_x, r * SQ_SIZE + board_start_y, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board, left_width, board_start_x, board_start_y):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE + left_width + board_start_x, r * SQ_SIZE + board_start_y, SQ_SIZE, SQ_SIZE))

def drawMoveLog(screen, gs, font):
    logScreen = p.Rect(0, BOARD_HEIGHT, 950, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), logScreen)

    chessLog = gs.moveLog
    moveInfo = [f"{i // 2 + 1}. {chessLog[i].getChessNotation()}  {chessLog[i + 1].getChessNotation()}" if i + 1 < len(
        chessLog) else f"{i // 2 + 1}. {chessLog[i].getChessNotation()}" for i in range(0, len(chessLog), 2)]
    textIndent = 10
    dataRow = 6
    y_axis = textIndent
    for i in range(0, len(moveInfo), dataRow):
        spacing = "  ".join(moveInfo[i:i + dataRow])
        textData = font.render(spacing, True, p.Color("white"))
        textLocation = logScreen.move(textIndent, y_axis)
        screen.blit(textData, textLocation)
        y_axis += textData.get_height()

def drawTimers(screen, font):
    global white_timer, black_timer
    width = 78
    height = 50

    neon_red = p.Color("#FF0000")
    white_timer_font = font.render(f"{round(white_timer) // 60:02d}:{round(white_timer) % 60:02d}", True, neon_red)
    black_timer_font = font.render(f"{round(black_timer) // 60:02d}:{round(black_timer) % 60:02d}", True, neon_red)
    white_timer_rect = white_timer_font.get_rect(bottomright=(BOARD_WIDTH + LEFT_PANEL_WIDTH + RIGHT_PANEL_WIDTH - 241, BOARD_HEIGHT + MOVE_LOG_PANEL_HEIGHT - 108))
    black_timer_rect = black_timer_font.get_rect(bottomright=(BOARD_WIDTH + LEFT_PANEL_WIDTH + RIGHT_PANEL_WIDTH - 623, BOARD_HEIGHT + MOVE_LOG_PANEL_HEIGHT - 624))

    white_timer_background_rect = white_timer_rect.inflate(10, 5)
    p.draw.rect(screen, p.Color("white"), white_timer_background_rect)
    black_timer_background_rect = black_timer_rect.inflate(12, 5)
    p.draw.rect(screen, p.Color("black"), black_timer_background_rect)

    screen.blit(white_timer_font, white_timer_rect)
    screen.blit(black_timer_font, black_timer_rect)
    clockImage = p.image.load("clockFrame.png")
    clockLogo = p.image.load("clockImg.png")

    clockImage = p.transform.scale(clockImage, (width, height))
    clockLogo = p.transform.scale(clockLogo, (30, 30))

    screen.blit(clockImage, (white_timer_rect.left - 15, white_timer_rect.centery - 25))
    screen.blit(clockImage, (black_timer_rect.left - 15, black_timer_rect.centery - 25))
    screen.blit(clockLogo, (white_timer_rect.left - 45, white_timer_rect.centery - 16))
    screen.blit(clockLogo, (black_timer_rect.left - 45, black_timer_rect.centery - 16))

def soundEffects(move):
    if move.pieceCaptured != "--":
        p.mixer.music.load("audio/Gotcha.mp3")
    elif move.pieceMoved == "wp" or move.pieceMoved == "bp":
        p.mixer.music.load("audio/Squeaky.mp3")
    elif move.pieceMoved == "wR" or move.pieceMoved == "bR":
        p.mixer.music.load("audio/Castle.mp3")
    elif move.pieceMoved == "wN" or move.pieceMoved == "bN":
        p.mixer.music.load("audio/Horse.mp3")
    elif move.pieceMoved == "wB" or move.pieceMoved == "bB":
        p.mixer.music.load("audio/Knife.mp3")
    elif move.pieceMoved == "wQ" or move.pieceMoved == "bQ":
        p.mixer.music.load("audio/Meep.mp3")
    elif move.pieceMoved == "wK" or move.pieceMoved == "bK":
        p.mixer.music.load("audio/Run.mp3")

    p.mixer.music.play()

    if move.pieceCaptured != "--":
        captured_pieces[move.pieceCaptured[0]].append(move.pieceCaptured)

def timerSoundEffect():
    p.mixer.music.load("audio/TimeLoser.mp3")
    p.mixer.music.play()

def winnerSoundEffect():
    p.mixer.music.load("audio/GoodEnding.mp3")
    p.mixer.music.play()

def highlightSquares(screen, gs, validMoves, sqSelected):
    x_axis = 36
    y_axis = 34

    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            x_center = c * SQ_SIZE + SQ_SIZE // 2 + LEFT_PANEL_WIDTH
            y_center = r * SQ_SIZE + SQ_SIZE // 2

            highlight_x = x_center - SQ_SIZE // 2 + x_axis
            highlight_y = y_center - SQ_SIZE // 2 + y_axis

            s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            s.set_alpha(110)
            s.fill(p.Color('yellow'))
            screen.blit(s, (highlight_x, highlight_y))

            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    end_r, end_c = move.endRow, move.endCol
                    x_center = end_c * SQ_SIZE + SQ_SIZE // 2 + LEFT_PANEL_WIDTH
                    y_center = end_r * SQ_SIZE + SQ_SIZE // 2

                    highlight_x = x_center - SQ_SIZE // 2 + x_axis
                    highlight_y = y_center - SQ_SIZE // 2 + y_axis

                    s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                    s.set_alpha(110)
                    s.fill(p.Color('purple'))
                    screen.blit(s, (highlight_x, highlight_y))

def drawGraveyard(screen, side, rect):
    global IMAGES
    SIZE = 50
    x_axis = 20
    y_axis = 10

    captured_pieces_list = captured_pieces[side]
    for piece_name in captured_pieces_list:
        if piece_name in IMAGES:
            piece_image = p.transform.scale(IMAGES[piece_name], (SIZE, SIZE))
            image_location = rect.move(x_axis, y_axis)
            screen.blit(piece_image, image_location)
            x_axis += SIZE + 10
            if x_axis + SIZE > rect.width - 10:
                x_axis = 20
                y_axis += SIZE + 10

                if y_axis + SIZE > rect.height - 10:
                    break

def drawCapturedPieces(screen):
    leftGraveyard = p.Rect(0, 0, LEFT_PANEL_WIDTH, PANEL_HEIGHT)
    rightGraveyard = p.Rect(BOARD_WIDTH + LEFT_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, PANEL_HEIGHT)

    drawGraveyard(screen, 'w', leftGraveyard)
    drawGraveyard(screen, 'b', rightGraveyard)

def updateCapturedPiecesOnUndo(last_move):
    if last_move.pieceCaptured != "--":
        captured_pieces[last_move.pieceCaptured[0]].remove(last_move.pieceCaptured)

def drawEndGameText(screen, text):

    y_axis = 60
    font = p.font.SysFont("Free Sans Bold", 40, True, False)
    textObject = font.render(text, False, p.Color('White'))
    text_rect = textObject.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - y_axis))
    screen.blit(textObject, text_rect)

    textObject = font.render(text, False, p.Color("Black"))
    text_rect = textObject.get_rect(center=(screen.get_width() // 2 + 2, screen.get_height() // 2 - y_axis + 2))
    screen.blit(textObject, text_rect)


if __name__ == "__main__":
    main()
