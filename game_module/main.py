import copy

import pygame
import math
from random import randrange
import random

from support.paths import (
    BOARD_PATH,
    ELEMENT_PATH,
    TEXT_PATH,
    MUSIC_PATH,
    DATA_PATH,
    text_one_up,
    text_high_score,
    ready,
    characters,
    character_title,
    pacman_title,
    wall,
    credit,
    instructions,
    event,
)
from support.playable_variables import (
    screen,
    square,
    sprite_offset,
    sprite_ratio,
    original_game_board,
    pellet_color,
    PLAYING_KEYS,
    game_board,
)

pygame.mixer.init()
pygame.init()
pygame.display.flip()


class Game:
    def __init__(self, level, score):
        self.paused = True
        self.ghostUpdateDelay = 1
        self.ghostUpdateCount = 0
        self.pacmanUpdateDelay = 1
        self.pacmanUpdateCount = 0
        self.tictakChangeDelay = 10
        self.tictakChangeCount = 0
        self.ghostsAttacked = False
        self.highScore = self.getHighScore()
        self.score = score
        self.level = level
        self.lives = 3
        self.ghosts = [
            Ghost(14.0, 13.5, "red", 0),
            Ghost(17.0, 11.5, "blue", 1),
            Ghost(17.0, 13.5, "pink", 2),
            Ghost(17.0, 15.5, "orange", 3),
        ]
        self.pacman = Pacman(26.0, 13.5)  # Center of Second Last Row
        self.total = self.getCount()
        self.ghostScore = 200
        self.levels = [[350, 250], [150, 450], [150, 450], [0, 600]]
        random.shuffle(self.levels)
        # Level index and Level Progress
        self.ghostStates = [[1, 0], [0, 0], [1, 0], [0, 0]]
        index = 0
        for state in self.ghostStates:
            state[0] = randrange(2)
            state[1] = randrange(self.levels[index][state[0]] + 1)
            index += 1
        self.collected = 0
        self.started = False
        self.gameOver = False
        self.gameOverCounter = 0
        self.points = []
        self.pointsTimer = 10
        # Berry Spawn Time, Berry Death Time, Berry Eaten
        self.berryState = [200, 400, False]
        self.berryLocation = [20.0, 13.5]
        self.berries = [
            "tile080.png",
            "tile081.png",
            "tile082.png",
            "tile083.png",
            "tile084.png",
            "tile085.png",
            "tile086.png",
            "tile087.png",
        ]
        self.berriesCollected = []
        self.levelTimer = 0
        self.berryScore = 100
        self.lockedInTimer = 100
        self.lockedIn = True
        self.extraLifeGiven = False
        self.music_playing = 0

    # Driver method: The games primary update method
    def update(self):
        # pygame.image.unload()
        print(self.ghostStates)
        if self.gameOver:
            self.gameOverFunc()
            return
        if self.paused or not self.started:
            self.handlePausedOrNotStarted()
            return

        self.updateTimers()

        if self.score >= 10000 and not self.extraLifeGiven:
            self.lives += 1
            self.extraLifeGiven = True
            self.forcePlayMusic("pacman_extrapac.wav")

        # Draw tiles around ghosts and pacman
        self.clearBoard()
        for ghost in self.ghosts:
            if ghost.attacked:
                self.ghostsAttacked = True

        # Check if the ghost should case pacman
        index = 0
        for state in self.ghostStates:
            state[1] += 1
            if state[1] >= self.levels[index][state[0]]:
                state[1] = 0
                state[0] += 1
                state[0] %= 2
            index += 1

        index = 0
        for ghost in self.ghosts:
            if (
                not ghost.attacked
                and not ghost.dead
                and self.ghostStates[index][0] == 0
            ):
                ghost.target = [self.pacman.row, self.pacman.col]
            index += 1

        if self.levelTimer == self.lockedInTimer:
            self.lockedIn = False

        self.checkSurroundings()
        if self.ghostUpdateCount == self.ghostUpdateDelay:
            for ghost in self.ghosts:
                ghost.update()
            self.ghostUpdateCount = 0

        if self.tictakChangeCount == self.tictakChangeDelay:
            # Changes the color of special Tic-Taks
            self.flipColor()
            self.tictakChangeCount = 0

        if self.pacmanUpdateCount == self.pacmanUpdateDelay:
            self.update_sup()
        self.checkSurroundings()
        self.highScore = max(self.score, self.highScore)

        global running
        if self.collected == self.total:
            print("New Level")
            self.forcePlayMusic("intermission.wav")
            self.level += 1
            self.newLevel()

        if self.level - 1 == 8:  # (self.levels[0][0] + self.levels[0][1]) // 50:
            print("You win", self.level, len(self.levels))
            running = False
        self.softRender()

    def handlePausedOrNotStarted(self):
        self.drawTilesAround(21, 10)
        self.drawTilesAround(21, 11)
        self.drawTilesAround(21, 12)
        self.drawTilesAround(21, 13)
        self.drawTilesAround(21, 14)
        self.drawReady()
        pygame.display.update()

    def updateTimers(self):
        self.levelTimer += 1
        self.ghostUpdateCount += 1
        self.pacmanUpdateCount += 1
        self.tictakChangeCount += 1
        self.ghostsAttacked = False

    def update_sup(self):
        self.pacmanUpdateCount = 0
        self.pacman.update()
        self.pacman.col %= len(game_board[0])
        if self.pacman.row % 1.0 == 0 and self.pacman.col % 1.0 == 0:
            if game_board[int(self.pacman.row)][int(self.pacman.col)] == 2:
                self.playMusic("munch_1.wav")
                game_board[int(self.pacman.row)][int(self.pacman.col)] = 1
                self.score += 10
                self.collected += 1
                # Fill tile with black
                pygame.draw.rect(
                    screen,
                    (0, 0, 0),
                    (
                        self.pacman.col * square,
                        self.pacman.row * square,
                        square,
                        square,
                    ),
                )
            elif (
                game_board[int(self.pacman.row)][int(self.pacman.col)] == 5
                or game_board[int(self.pacman.row)][int(self.pacman.col)] == 6
            ):
                self.forcePlayMusic("power_pellet.wav")
                game_board[int(self.pacman.row)][int(self.pacman.col)] = 1
                self.collected += 1
                # Fill tile with black
                pygame.draw.rect(
                    screen,
                    (0, 0, 0),
                    (
                        self.pacman.col * square,
                        self.pacman.row * square,
                        square,
                        square,
                    ),
                )
                self.score += 50
                self.ghostScore = 200
                for ghost in self.ghosts:
                    ghost.attackedCount = 0
                    ghost.setAttacked(True)
                    ghost.setTarget()
                    self.ghostsAttacked = True

    # Render method
    def render(self):
        screen.fill((0, 0, 0))  # Flushes the screen
        # Draws game elements
        currentTile = 0
        self.displayLives()
        self.displayScore()
        for i in range(3, len(game_board) - 2):
            for j in range(len(game_board[0])):
                if game_board[i][j] == 3:  # Draw wall
                    imageName = str(currentTile)
                    if len(imageName) == 1:
                        imageName = "00" + imageName
                    elif len(imageName) == 2:
                        imageName = "0" + imageName
                    # Get image of desired tile
                    imageName = "tile" + imageName + ".png"
                    tileImage = pygame.image.load(BOARD_PATH + imageName)
                    tileImage = pygame.transform.scale(tileImage, (square, square))

                    # Display image of tile
                    screen.blit(tileImage, (j * square, i * square, square, square))

                elif game_board[i][j] == 2:  # Draw Tic-Tak
                    pygame.draw.circle(
                        screen,
                        pellet_color,
                        (j * square + square // 2, i * square + square // 2),
                        square // 4,
                    )
                elif game_board[i][j] == 5:  # Black Special Tic-Tak
                    pygame.draw.circle(
                        screen,
                        (0, 0, 0),
                        (j * square + square // 2, i * square + square // 2),
                        square // 2,
                    )
                elif game_board[i][j] == 6:  # White Special Tic-Tak
                    pygame.draw.circle(
                        screen,
                        pellet_color,
                        (j * square + square // 2, i * square + square // 2),
                        square // 2,
                    )

                currentTile += 1
        # Draw Sprites
        for ghost in self.ghosts:
            ghost.draw()
        self.pacman.draw()
        # Updates the screen
        pygame.display.update()

    def softRender(self):
        pointsToDraw = []
        for point in self.points:
            if point[3] < self.pointsTimer:
                pointsToDraw.append([point[2], point[0], point[1]])
                point[3] += 1
            else:
                self.points.remove(point)
                self.drawTilesAround(point[0], point[1])

        for point in pointsToDraw:
            self.drawPoints(point[0], point[1], point[2])

        # Draw Sprites
        for ghost in self.ghosts:
            ghost.draw()
        self.pacman.draw()
        self.displayScore()
        self.displayBerries()
        self.displayLives()
        # for point in pointsToDraw:
        #     self.drawPoints(point[0], point[1], point[2])
        self.drawBerry()
        # Updates the screen
        pygame.display.update()

    def playMusic(self, music):
        # return False # Uncomment to disable music
        global music_playing
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.unload()
            pygame.mixer.music.load(MUSIC_PATH + music)
            pygame.mixer.music.queue(MUSIC_PATH + music)
            pygame.mixer.music.play()
            if music == "munch_1.wav":
                music_playing = 0
            elif music == "siren_1.wav":
                music_playing = 2
            else:
                music_playing = 1

    def forcePlayMusic(self, music):
        # return False # Uncomment to disable music
        pygame.mixer.music.unload()
        pygame.mixer.music.load(MUSIC_PATH + music)
        pygame.mixer.music.play()
        global music_playing
        music_playing = 1

    def clearBoard(self):
        # Draw tiles around ghosts and pacman
        for ghost in self.ghosts:
            self.drawTilesAround(ghost.row, ghost.col)
        self.drawTilesAround(self.pacman.row, self.pacman.col)
        self.drawTilesAround(self.berryLocation[0], self.berryLocation[1])
        # Clears Ready! Label
        self.drawTilesAround(20, 10)
        self.drawTilesAround(20, 11)
        self.drawTilesAround(20, 12)
        self.drawTilesAround(20, 13)
        self.drawTilesAround(20, 14)

    def checkSurroundings(self):
        # Check if pacman got killed
        for ghost in self.ghosts:
            if self.touchingPacman(ghost.row, ghost.col) and not ghost.attacked:
                if self.lives == 1:
                    print("You lose")
                    self.forcePlayMusic("death_1.wav")
                    self.gameOver = True
                    # Removes the ghosts from the screen
                    for ghost in self.ghosts:
                        self.drawTilesAround(ghost.row, ghost.col)
                    self.drawTilesAround(self.pacman.row, self.pacman.col)
                    self.pacman.draw()
                    pygame.display.update()
                    pause(10000000)
                    return
                self.started = False
                self.forcePlayMusic("pacman_death.wav")
                reset()
            elif (
                self.touchingPacman(ghost.row, ghost.col)
                and ghost.isAttacked()
                and not ghost.isDead()
            ):
                ghost.setDead(True)
                ghost.setTarget()
                ghost.ghostSpeed = 1
                ghost.row = math.floor(ghost.row)
                ghost.col = math.floor(ghost.col)
                self.score += self.ghostScore
                self.points.append([ghost.row, ghost.col, self.ghostScore, 0])
                self.ghostScore *= 2
                self.forcePlayMusic("eat_ghost.wav")
                pause(10000000)
        if (
            self.touchingPacman(self.berryLocation[0], self.berryLocation[1])
            and not self.berryState[2]
            and self.levelTimer in range(self.berryState[0], self.berryState[1])
        ):
            self.berryState[2] = True
            self.score += self.berryScore
            self.points.append(
                [self.berryLocation[0], self.berryLocation[1], self.berryScore, 0]
            )
            self.berriesCollected.append(self.berries[(self.level - 1) % 8])
            self.forcePlayMusic("eat_fruit.wav")

    # Displays the current score
    def displayScore(self):
        index = 0
        scoreStart = 5
        highScoreStart = 11
        for i in range(scoreStart, scoreStart + len(text_one_up)):
            tileImage = pygame.image.load(TEXT_PATH + text_one_up[index])
            tileImage = pygame.transform.scale(tileImage, (square, square))
            screen.blit(tileImage, (i * square, 4, square, square))
            index += 1
        score = str(self.score)
        if score == "0":
            score = "00"
        index = 0
        for i in range(0, len(score)):
            digit = int(score[i])
            tileImage = pygame.image.load(
                TEXT_PATH + "tile0" + str(32 + digit) + ".png"
            )
            tileImage = pygame.transform.scale(tileImage, (square, square))
            screen.blit(
                tileImage,
                ((scoreStart + 2 + index) * square, square + 4, square, square),
            )
            index += 1

        index = 0
        for i in range(highScoreStart, highScoreStart + len(text_high_score)):
            tileImage = pygame.image.load(TEXT_PATH + text_high_score[index])
            tileImage = pygame.transform.scale(tileImage, (square, square))
            screen.blit(tileImage, (i * square, 4, square, square))
            index += 1

        highScore = str(self.highScore)
        if highScore == "0":
            highScore = "00"
        index = 0
        for i in range(0, len(highScore)):
            digit = int(highScore[i])
            tileImage = pygame.image.load(
                TEXT_PATH + "tile0" + str(32 + digit) + ".png"
            )
            tileImage = pygame.transform.scale(tileImage, (square, square))
            screen.blit(
                tileImage,
                ((highScoreStart + 6 + index) * square, square + 4, square, square),
            )
            index += 1

    def drawBerry(self):
        if (
            self.levelTimer in range(self.berryState[0], self.berryState[1])
            and not self.berryState[2]
        ):
            # print("here")
            berryImage = pygame.image.load(
                ELEMENT_PATH + self.berries[(self.level - 1) % 8]
            )
            berryImage = pygame.transform.scale(
                berryImage, (int(square * sprite_ratio), int(square * sprite_ratio))
            )
            screen.blit(
                berryImage,
                (
                    self.berryLocation[1] * square,
                    self.berryLocation[0] * square,
                    square,
                    square,
                ),
            )

    def drawPoints(self, points, row, col):
        pointStr = str(points)
        index = 0
        for i in range(len(pointStr)):
            digit = int(pointStr[i])
            tileImage = pygame.image.load(
                TEXT_PATH + "tile" + str(224 + digit) + ".png"
            )
            tileImage = pygame.transform.scale(tileImage, (square // 2, square // 2))
            screen.blit(
                tileImage,
                (
                    (col) * square + (square // 2 * index),
                    row * square - 20,
                    square // 2,
                    square // 2,
                ),
            )
            index += 1

    def drawReady(self):
        for i in range(len(ready)):
            letter = pygame.image.load(TEXT_PATH + ready[i])
            letter = pygame.transform.scale(letter, (int(square), int(square)))
            screen.blit(letter, ((11 + i) * square, 20 * square, square, square))

    def gameOverFunc(self):
        global running
        if self.gameOverCounter == 12:
            running = False
            self.recordHighScore()
            return

        # Resets the screen around pacman
        self.drawTilesAround(self.pacman.row, self.pacman.col)

        # Draws new image
        pacmanImage = pygame.image.load(
            ELEMENT_PATH + "tile" + str(116 + self.gameOverCounter) + ".png"
        )
        pacmanImage = pygame.transform.scale(
            pacmanImage, (int(square * sprite_ratio), int(square * sprite_ratio))
        )
        screen.blit(
            pacmanImage,
            (
                self.pacman.col * square + sprite_offset,
                self.pacman.row * square + sprite_offset,
                square,
                square,
            ),
        )
        pygame.display.update()
        pause(5000000)
        self.gameOverCounter += 1

    def displayLives(self):
        # 33 rows || 28 cols
        # Lives[[31, 5], [31, 3], [31, 1]]
        livesLoc = [[34, 3], [34, 1]]
        for i in range(self.lives - 1):
            lifeImage = pygame.image.load(ELEMENT_PATH + "tile054.png")
            lifeImage = pygame.transform.scale(
                lifeImage, (int(square * sprite_ratio), int(square * sprite_ratio))
            )
            screen.blit(
                lifeImage,
                (
                    livesLoc[i][1] * square,
                    livesLoc[i][0] * square - sprite_offset,
                    square,
                    square,
                ),
            )

    def displayBerries(self):
        firstBerrie = [34, 26]
        for i in range(len(self.berriesCollected)):
            berrieImage = pygame.image.load(ELEMENT_PATH + self.berriesCollected[i])
            berrieImage = pygame.transform.scale(
                berrieImage, (int(square * sprite_ratio), int(square * sprite_ratio))
            )
            screen.blit(
                berrieImage,
                (
                    (firstBerrie[1] - (2 * i)) * square,
                    firstBerrie[0] * square + 5,
                    square,
                    square,
                ),
            )

    def touchingPacman(self, row, col):
        if (
            row - 0.5 <= self.pacman.row
            and row >= self.pacman.row
            and col == self.pacman.col
        ):
            return True
        elif (
            row + 0.5 >= self.pacman.row
            and row <= self.pacman.row
            and col == self.pacman.col
        ):
            return True
        elif (
            row == self.pacman.row
            and col - 0.5 <= self.pacman.col
            and col >= self.pacman.col
        ):
            return True
        elif (
            row == self.pacman.row
            and col + 0.5 >= self.pacman.col
            and col <= self.pacman.col
        ):
            return True
        elif row == self.pacman.row and col == self.pacman.col:
            return True
        return False

    def newLevel(self):
        reset()
        self.lives += 1
        self.collected = 0
        self.started = False
        self.berryState = [200, 400, False]
        self.levelTimer = 0
        self.lockedIn = True
        for level in self.levels:
            level[0] = min((level[0] + level[1]) - 100, level[0] + 50)
            level[1] = max(100, level[1] - 50)
        random.shuffle(self.levels)
        index = 0
        for state in self.ghostStates:
            state[0] = randrange(2)
            state[1] = randrange(self.levels[index][state[0]] + 1)
            index += 1
        global game_board
        game_board = copy.deepcopy(original_game_board)
        self.render()

    def drawTilesAround(self, row, col):
        row = math.floor(row)
        col = math.floor(col)
        for i in range(row - 2, row + 3):
            for j in range(col - 2, col + 3):
                if (
                    i >= 3
                    and i < len(game_board) - 2
                    and j >= 0
                    and j < len(game_board[0])
                ):
                    imageName = str(((i - 3) * len(game_board[0])) + j)
                    if len(imageName) == 1:
                        imageName = "00" + imageName
                    elif len(imageName) == 2:
                        imageName = "0" + imageName
                    # Get image of desired tile
                    imageName = "tile" + imageName + ".png"
                    tileImage = pygame.image.load(BOARD_PATH + imageName)
                    tileImage = pygame.transform.scale(tileImage, (square, square))
                    # Display image of tile
                    screen.blit(tileImage, (j * square, i * square, square, square))

                    if game_board[i][j] == 2:  # Draw Tic-Tak
                        pygame.draw.circle(
                            screen,
                            pellet_color,
                            (j * square + square // 2, i * square + square // 2),
                            square // 4,
                        )
                    elif game_board[i][j] == 5:  # Black Special Tic-Tak
                        pygame.draw.circle(
                            screen,
                            (0, 0, 0),
                            (j * square + square // 2, i * square + square // 2),
                            square // 2,
                        )
                    elif game_board[i][j] == 6:  # White Special Tic-Tak
                        pygame.draw.circle(
                            screen,
                            pellet_color,
                            (j * square + square // 2, i * square + square // 2),
                            square // 2,
                        )

    # Flips Color of Special Tic-Taks
    def flipColor(self):
        global game_board
        for i in range(3, len(game_board) - 2):
            for j in range(len(game_board[0])):
                if game_board[i][j] == 5:
                    game_board[i][j] = 6
                    pygame.draw.circle(
                        screen,
                        pellet_color,
                        (j * square + square // 2, i * square + square // 2),
                        square // 2,
                    )
                elif game_board[i][j] == 6:
                    game_board[i][j] = 5
                    pygame.draw.circle(
                        screen,
                        (0, 0, 0),
                        (j * square + square // 2, i * square + square // 2),
                        square // 2,
                    )

    def getCount(self):
        total = 0
        for i in range(3, len(game_board) - 2):
            for j in range(len(game_board[0])):
                if (
                    game_board[i][j] == 2
                    or game_board[i][j] == 5
                    or game_board[i][j] == 6
                ):
                    total += 1
        return total

    def getHighScore(self):
        file = open(DATA_PATH + "HighScore.txt", "r")
        highScore = int(file.read())
        file.close()
        return highScore

    def recordHighScore(self):
        file = open(DATA_PATH + "HighScore.txt", "w").close()
        file = open(DATA_PATH + "HighScore.txt", "w+")
        file.write(str(self.highScore))
        file.close()


class Pacman:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.mouthOpen = False
        self.pacSpeed = 1 / 4
        self.mouthChangeDelay = 5
        self.mouthChangeCount = 0
        self.dir = 0  # 0: North, 1: East, 2: South, 3: West
        self.newDir = 0

    def update(self):
        if self.newDir == 0:
            if (
                can_move(math.floor(self.row - self.pacSpeed), self.col)
                and self.col % 1.0 == 0
            ):
                self.row -= self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 1:
            if (
                can_move(self.row, math.ceil(self.col + self.pacSpeed))
                and self.row % 1.0 == 0
            ):
                self.col += self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 2:
            if (
                can_move(math.ceil(self.row + self.pacSpeed), self.col)
                and self.col % 1.0 == 0
            ):
                self.row += self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 3:
            if (
                can_move(self.row, math.floor(self.col - self.pacSpeed))
                and self.row % 1.0 == 0
            ):
                self.col -= self.pacSpeed
                self.dir = self.newDir
                return

        if self.dir == 0:
            if (
                can_move(math.floor(self.row - self.pacSpeed), self.col)
                and self.col % 1.0 == 0
            ):
                self.row -= self.pacSpeed
        elif self.dir == 1:
            if (
                can_move(self.row, math.ceil(self.col + self.pacSpeed))
                and self.row % 1.0 == 0
            ):
                self.col += self.pacSpeed
        elif self.dir == 2:
            if (
                can_move(math.ceil(self.row + self.pacSpeed), self.col)
                and self.col % 1.0 == 0
            ):
                self.row += self.pacSpeed
        elif self.dir == 3:
            if (
                can_move(self.row, math.floor(self.col - self.pacSpeed))
                and self.row % 1.0 == 0
            ):
                self.col -= self.pacSpeed

    # Draws pacman based on his current state
    def draw(self):
        if not game.started:
            pacmanImage = pygame.image.load(ELEMENT_PATH + "tile112.png")
            pacmanImage = pygame.transform.scale(
                pacmanImage, (int(square * sprite_ratio), int(square * sprite_ratio))
            )
            screen.blit(
                pacmanImage,
                (
                    self.col * square + sprite_offset,
                    self.row * square + sprite_offset,
                    square,
                    square,
                ),
            )
            return

        if self.mouthChangeCount == self.mouthChangeDelay:
            self.mouthChangeCount = 0
            self.mouthOpen = not self.mouthOpen
        self.mouthChangeCount += 1
        # pacmanImage = pygame.image.load("Sprites/tile049.png")
        if self.dir == 0:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(ELEMENT_PATH + "tile049.png")
            else:
                pacmanImage = pygame.image.load(ELEMENT_PATH + "tile051.png")
        elif self.dir == 1:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(ELEMENT_PATH + "tile052.png")
            else:
                pacmanImage = pygame.image.load(ELEMENT_PATH + "tile054.png")
        elif self.dir == 2:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(ELEMENT_PATH + "tile053.png")
            else:
                pacmanImage = pygame.image.load(ELEMENT_PATH + "tile055.png")
        elif self.dir == 3:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(ELEMENT_PATH + "tile048.png")
            else:
                pacmanImage = pygame.image.load(ELEMENT_PATH + "tile050.png")

        pacmanImage = pygame.transform.scale(
            pacmanImage, (int(square * sprite_ratio), int(square * sprite_ratio))
        )
        screen.blit(
            pacmanImage,
            (
                self.col * square + sprite_offset,
                self.row * square + sprite_offset,
                square,
                square,
            ),
        )


class Ghost:
    def __init__(self, row, col, color, changeFeetCount):
        self.row = row
        self.col = col
        self.attacked = False
        self.color = color
        self.dir = randrange(4)
        self.dead = False
        self.changeFeetCount = changeFeetCount
        self.changeFeetDelay = 5
        self.target = [-1, -1]
        self.ghostSpeed = 1 / 4
        self.lastLoc = [-1, -1]
        self.attackedTimer = 240
        self.attackedCount = 0
        self.deathTimer = 120
        self.deathCount = 0

    def update(self):
        # print(self.row, self.col)
        if (
            self.target == [-1, -1]
            or (self.row == self.target[0] and self.col == self.target[1])
            or game_board[int(self.row)][int(self.col)] == 4
            or self.dead
        ):
            self.setTarget()
        self.setDir()
        self.move()

        if self.attacked:
            self.attackedCount += 1

        if self.attacked and not self.dead:
            self.ghostSpeed = 1 / 8

        if self.attackedCount == self.attackedTimer and self.attacked:
            if not self.dead:
                self.ghostSpeed = 1 / 4
                self.row = math.floor(self.row)
                self.col = math.floor(self.col)

            self.attackedCount = 0
            self.attacked = False
            self.setTarget()

        if self.dead and game_board[self.row][self.col] == 4:
            self.deathCount += 1
            self.attacked = False
            if self.deathCount == self.deathTimer:
                self.deathCount = 0
                self.dead = False
                self.ghostSpeed = 1 / 4

    def draw(
        self,
    ):  # Ghosts states: Alive, Attacked, Dead Attributes: Color, Direction, Location
        ghostImage = pygame.image.load(ELEMENT_PATH + "tile152.png")
        currentDir = ((self.dir + 3) % 4) * 2
        if self.changeFeetCount == self.changeFeetDelay:
            self.changeFeetCount = 0
            currentDir += 1
        self.changeFeetCount += 1
        if self.dead:
            tileNum = 152 + currentDir
            ghostImage = pygame.image.load(
                ELEMENT_PATH + "tile" + str(tileNum) + ".png"
            )
        elif self.attacked:
            if self.attackedTimer - self.attackedCount < self.attackedTimer // 3:
                if (self.attackedTimer - self.attackedCount) % 31 < 26:
                    ghostImage = pygame.image.load(
                        ELEMENT_PATH
                        + "tile0"
                        + str(70 + (currentDir - (((self.dir + 3) % 4) * 2)))
                        + ".png"
                    )
                else:
                    ghostImage = pygame.image.load(
                        ELEMENT_PATH
                        + "tile0"
                        + str(72 + (currentDir - (((self.dir + 3) % 4) * 2)))
                        + ".png"
                    )
            else:
                ghostImage = pygame.image.load(
                    ELEMENT_PATH
                    + "tile0"
                    + str(72 + (currentDir - (((self.dir + 3) % 4) * 2)))
                    + ".png"
                )
        else:
            if self.color == "blue":
                tileNum = 136 + currentDir
                ghostImage = pygame.image.load(
                    ELEMENT_PATH + "tile" + str(tileNum) + ".png"
                )
            elif self.color == "pink":
                tileNum = 128 + currentDir
                ghostImage = pygame.image.load(
                    ELEMENT_PATH + "tile" + str(tileNum) + ".png"
                )
            elif self.color == "orange":
                tileNum = 144 + currentDir
                ghostImage = pygame.image.load(
                    ELEMENT_PATH + "tile" + str(tileNum) + ".png"
                )
            elif self.color == "red":
                tileNum = 96 + currentDir
                if tileNum < 100:
                    ghostImage = pygame.image.load(
                        ELEMENT_PATH + "tile0" + str(tileNum) + ".png"
                    )
                else:
                    ghostImage = pygame.image.load(
                        ELEMENT_PATH + "tile" + str(tileNum) + ".png"
                    )

        ghostImage = pygame.transform.scale(
            ghostImage, (int(square * sprite_ratio), int(square * sprite_ratio))
        )
        screen.blit(
            ghostImage,
            (
                self.col * square + sprite_offset,
                self.row * square + sprite_offset,
                square,
                square,
            ),
        )

    def isValidTwo(self, cRow, cCol, dist, visited):
        if (
            cRow < 3
            or cRow >= len(game_board) - 5
            or cCol < 0
            or cCol >= len(game_board[0])
            or game_board[cRow][cCol] == 3
        ):
            return False
        elif visited[cRow][cCol] <= dist:
            return False
        return True

    def isValid(self, cRow, cCol):
        if cCol < 0 or cCol > len(game_board[0]) - 1:
            return True
        for ghost in game.ghosts:
            if ghost.color == self.color:
                continue
            if ghost.row == cRow and ghost.col == cCol and not self.dead:
                return False
        if not ghost_gate.count([cRow, cCol]) == 0:
            if self.dead and self.row < cRow:
                return True
            elif (
                self.row > cRow
                and not self.dead
                and not self.attacked
                and not game.lockedIn
            ):
                return True
            else:
                return False
        if game_board[cRow][cCol] == 3:
            return False
        return True

    def setDir(self):  # Very inefficient || can easily refactor
        # BFS search -> Not best route but a route none the less
        dirs = [
            [0, -self.ghostSpeed, 0],
            [1, 0, self.ghostSpeed],
            [2, self.ghostSpeed, 0],
            [3, 0, -self.ghostSpeed],
        ]
        random.shuffle(dirs)
        best = 10000
        bestDir = -1
        for newDir in dirs:
            if (
                self.calcDistance(
                    self.target, [self.row + newDir[1], self.col + newDir[2]]
                )
                < best
            ):
                if not (
                    self.lastLoc[0] == self.row + newDir[1]
                    and self.lastLoc[1] == self.col + newDir[2]
                ):
                    if newDir[0] == 0 and self.col % 1.0 == 0:
                        if self.isValid(
                            math.floor(self.row + newDir[1]), int(self.col + newDir[2])
                        ):
                            bestDir = newDir[0]
                            best = self.calcDistance(
                                self.target,
                                [self.row + newDir[1], self.col + newDir[2]],
                            )
                    elif newDir[0] == 1 and self.row % 1.0 == 0:
                        if self.isValid(
                            int(self.row + newDir[1]), math.ceil(self.col + newDir[2])
                        ):
                            bestDir = newDir[0]
                            best = self.calcDistance(
                                self.target,
                                [self.row + newDir[1], self.col + newDir[2]],
                            )
                    elif newDir[0] == 2 and self.col % 1.0 == 0:
                        if self.isValid(
                            math.ceil(self.row + newDir[1]), int(self.col + newDir[2])
                        ):
                            bestDir = newDir[0]
                            best = self.calcDistance(
                                self.target,
                                [self.row + newDir[1], self.col + newDir[2]],
                            )
                    elif newDir[0] == 3 and self.row % 1.0 == 0:
                        if self.isValid(
                            int(self.row + newDir[1]), math.floor(self.col + newDir[2])
                        ):
                            bestDir = newDir[0]
                            best = self.calcDistance(
                                self.target,
                                [self.row + newDir[1], self.col + newDir[2]],
                            )
        self.dir = bestDir

    def calcDistance(self, a, b):
        dR = a[0] - b[0]
        dC = a[1] - b[1]
        return math.sqrt((dR * dR) + (dC * dC))

    def setTarget(self):
        if game_board[int(self.row)][int(self.col)] == 4 and not self.dead:
            self.target = [ghost_gate[0][0] - 1, ghost_gate[0][1] + 1]
            return
        elif game_board[int(self.row)][int(self.col)] == 4 and self.dead:
            self.target = [self.row, self.col]
        elif self.dead:
            self.target = [14, 13]
            return

        # Records the quadrants of each ghost's target
        quads = [0, 0, 0, 0]
        for ghost in game.ghosts:
            # if ghost.target[0] == self.row and ghost.col == self.col:
            #     continue
            if ghost.target[0] <= 15 and ghost.target[1] >= 13:
                quads[0] += 1
            elif ghost.target[0] <= 15 and ghost.target[1] < 13:
                quads[1] += 1
            elif ghost.target[0] > 15 and ghost.target[1] < 13:
                quads[2] += 1
            elif ghost.target[0] > 15 and ghost.target[1] >= 13:
                quads[3] += 1

        # Finds a target that will keep the ghosts dispersed
        while True:
            self.target = [randrange(31), randrange(28)]
            quad = 0
            if self.target[0] <= 15 and self.target[1] >= 13:
                quad = 0
            elif self.target[0] <= 15 and self.target[1] < 13:
                quad = 1
            elif self.target[0] > 15 and self.target[1] < 13:
                quad = 2
            elif self.target[0] > 15 and self.target[1] >= 13:
                quad = 3
            if (
                not game_board[self.target[0]][self.target[1]] == 3
                and not game_board[self.target[0]][self.target[1]] == 4
            ):
                break
            elif quads[quad] == 0:
                break

    def move(self):
        # print(self.target)
        self.lastLoc = [self.row, self.col]
        if self.dir == 0:
            self.row -= self.ghostSpeed
        elif self.dir == 1:
            self.col += self.ghostSpeed
        elif self.dir == 2:
            self.row += self.ghostSpeed
        elif self.dir == 3:
            self.col -= self.ghostSpeed

        # Incase they go through the middle tunnel
        self.col = self.col % len(game_board[0])
        if self.col < 0:
            self.col = len(game_board[0]) - 0.5

    def setAttacked(self, isAttacked):
        self.attacked = isAttacked

    def isAttacked(self):
        return self.attacked

    def setDead(self, isDead):
        self.dead = isDead

    def isDead(self):
        return self.dead


game = Game(1, 0)
ghost_safe_area = [15, 13]  # The location the ghosts escape to when attacked
ghost_gate = [[15, 13], [15, 14]]


def can_move(row, col):
    if col == -1 or col == len(game_board[0]):
        return True
    if game_board[int(row)][int(col)] != 3:
        return True
    return False


# Reset after death
def reset():
    global game
    game.ghosts = [
        Ghost(14.0, 13.5, "red", 0),
        Ghost(17.0, 11.5, "blue", 1),
        Ghost(17.0, 13.5, "pink", 2),
        Ghost(17.0, 15.5, "orange", 3),
    ]
    for ghost in game.ghosts:
        ghost.setTarget()
    game.pacman = Pacman(26.0, 13.5)
    game.lives -= 1
    game.paused = True
    game.render()


def display_launch_screen():
    # Draw Pacman Title
    for i in range(len(pacman_title)):
        letter = pygame.image.load(TEXT_PATH + pacman_title[i])
        letter = pygame.transform.scale(letter, (int(square * 4), int(square * 4)))
        screen.blit(letter, ((2 + 4 * i) * square, 2 * square, square, square))

    for i in range(len(character_title)):
        letter = pygame.image.load(TEXT_PATH + character_title[i])
        letter = pygame.transform.scale(letter, (int(square), int(square)))
        screen.blit(letter, ((4 + i) * square, 10 * square, square, square))

    for i in range(len(characters)):
        for j in range(len(characters[i])):
            if j == 0:
                letter = pygame.image.load(TEXT_PATH + characters[i][j])
                letter = pygame.transform.scale(
                    letter, (int(square * sprite_ratio), int(square * sprite_ratio))
                )
                screen.blit(
                    letter,
                    (
                        (2 + j) * square - square // 2,
                        (12 + 2 * i) * square - square // 3,
                        square,
                        square,
                    ),
                )
            else:
                letter = pygame.image.load(TEXT_PATH + characters[i][j])
                letter = pygame.transform.scale(letter, (int(square), int(square)))
                screen.blit(
                    letter, ((2 + j) * square, (12 + 2 * i) * square, square, square)
                )
    # Draw Pacman and Ghosts
    for i in range(len(event)):
        character = pygame.image.load(TEXT_PATH + event[i])
        character = pygame.transform.scale(
            character, (int(square * 2), int(square * 2))
        )
        screen.blit(character, ((4 + i * 2) * square, 24 * square, square, square))
    # Draw PlatForm from Pacman and Ghosts
    for i in range(len(wall)):
        platform = pygame.image.load(TEXT_PATH + wall[i])
        platform = pygame.transform.scale(platform, (int(square * 2), int(square * 2)))
        screen.blit(platform, ((i * 2) * square, 26 * square, square, square))
    # Credit myself
    for i in range(len(credit)):
        letter = pygame.image.load(TEXT_PATH + credit[i])
        letter = pygame.transform.scale(letter, (int(square), int(square)))
        screen.blit(letter, ((6 + i) * square, 30 * square, square, square))
    # Press Space to Play
    for i in range(len(instructions)):
        letter = pygame.image.load(TEXT_PATH + instructions[i])
        letter = pygame.transform.scale(letter, (int(square), int(square)))
        screen.blit(letter, ((4.5 + i) * square, 35 * square - 10, square, square))

    pygame.display.update()


running = True
on_launch_screen = True
display_launch_screen()
clock = pygame.time.Clock()


def pause(time):
    cur = 0
    while not cur == time:
        cur += 1


while running:
    clock.tick(40)
    for user_event in pygame.event.get():
        if user_event.type == pygame.QUIT:
            running = False
            game.recordHighScore()
        elif user_event.type == pygame.KEYDOWN:
            game.paused = False
            game.started = True
            if user_event.key in PLAYING_KEYS["up"]:
                if not on_launch_screen:
                    game.pacman.newDir = 0
            elif user_event.key in PLAYING_KEYS["right"]:
                if not on_launch_screen:
                    game.pacman.newDir = 1
            elif user_event.key in PLAYING_KEYS["down"]:
                if not on_launch_screen:
                    game.pacman.newDir = 2
            elif user_event.key in PLAYING_KEYS["left"]:
                if not on_launch_screen:
                    game.pacman.newDir = 3
            elif user_event.key == pygame.K_SPACE:
                if on_launch_screen:
                    on_launch_screen = False
                    game.paused = True
                    game.started = False
                    game.render()
                    pygame.mixer.music.load(MUSIC_PATH + "pacman_beginning.wav")
                    pygame.mixer.music.play()
                    music_playing = 1
            elif user_event.key == pygame.K_q:
                running = False
                game.recordHighScore()

    if not on_launch_screen:
        game.update()
