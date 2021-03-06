from enemyManager import EnemyManager
from projectileManager import ProjectileManager
from Tiles.tile import Dir
from Tiles.towerTile import TowerTile
import tileFactory
import math
import random
import pygame


class Grid:
    x = 0
    y = 0
    rows = 0
    cols = 0
    tileSize = 0
    grid = []
    start = (0, 0)
    linesOn = False
    borderWidth = 3

    def __init__(self, startPos, startDims, tileSize):
        self.x = startPos[0]
        self.y = startPos[1]
        self.rows = startDims[0]
        self.cols = startDims[1]
        self.tileSize = tileSize
        self.enemyManager = EnemyManager(self)
        self.projectileManager = ProjectileManager()
        self.regenerateGrid()

    def draw(self, screen):
        pygame.draw.rect(screen, (150, 150, 150), (self.x - self.borderWidth, self.y - self.borderWidth, self.tileSize * self.cols + 2*self.borderWidth, self.tileSize * self.rows + 2*self.borderWidth))
        pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.tileSize * self.cols, self.tileSize * self.rows))
        selected = None
        for i in range(0, self.cols):
            for j in range(0, self.rows):
                if self.grid[i][j].selected:
                    selected = self.grid[i][j]
                else:
                    self.grid[i][j].draw(screen)

        if self.linesOn:
            for i in range(1, self.cols):
                pygame.draw.line(screen, (150, 150, 150), (self.x + self.tileSize * i, self.y), (self.x + self.tileSize * i, self.y + self.tileSize * self.rows))
            for i in range(1, self.rows):
                pygame.draw.line(screen, (150, 150, 150), (self.x, self.y + self.tileSize * i), (self.x + self.tileSize * self.cols, self.y + self.tileSize * i))
        self.enemyManager.draw(screen)
        self.projectileManager.draw(screen)
        if selected is not None:
            selected.draw(screen)

    def startWave(self):
        self.enemyManager.spawnEnemy(self.grid[self.start[0]][self.start[1]])

    def update(self):
        deadEnemies = self.enemyManager.update()
        for enemy in deadEnemies:
            self.projectileManager.despawnProjectilesForEnemy(enemy)
        for i in range(0, self.cols):
            for j in range(0, self.rows):
                shot = self.grid[i][j].update()
                if shot is not None:
                    self.projectileManager.addProjectile(shot)
        self.projectileManager.update()

    def isInGrid(self, pos):
        if self.x + self.borderWidth <= pos[0] <= self.x + self.tileSize * self.cols - self.borderWidth:
            if self.y + self.borderWidth <= pos[1] <= self.y + self.tileSize * self.rows - self.borderWidth:
                return True
        return False

    def setTile(self, row, col, tile):
        tile.x = self.x + self.tileSize * row
        tile.y = self.y + self.tileSize * col
        tile.size = self.tileSize
        self.grid[row][col] = tile
        for row in self.grid:
            for cTile in row:
                if issubclass(cTile.__class__, TowerTile):
                    cTile.updateViewableTiles(self.grid)

    def setTileAtPos(self, pos, tile):
        xDist = pos[0] - self.x
        yDist = pos[1] - self.y
        col = math.floor(xDist / self.tileSize)
        row = math.floor(yDist / self.tileSize)
        self.setTile(col, row, tile)

    def getTileAtPos(self, pos):
        xDist = pos[0] - self.x
        yDist = pos[1] - self.y
        col = math.floor(xDist / self.tileSize)
        row = math.floor(yDist / self.tileSize)
        return self.grid[col][row]

    def isPlaceableAtPos(self, pos):
        try:
            xDist = pos[0] - self.x
            yDist = pos[1] - self.y
            col = math.floor(xDist / self.tileSize)
            row = math.floor(yDist / self.tileSize)
            if (not self.grid[col][row].isRoad) and (not self.grid[col][row].isTower):
                return True
            return False
        except:
            return False

    def showLines(self, show):
        self.linesOn = show

    def regenerateGrid(self):
        self.grid = []
        for i in range(0, self.cols):
            self.grid.append([])
            for j in range(0, self.rows):
                self.grid[i].append(
                    tileFactory.getTile("empty", self.x + self.tileSize * i, self.y + self.tileSize * j, self.tileSize))

        self.constructRoad(18)
        self.projectileManager.despawnProjectiles()
        self.enemyManager.despawnEnemies()

    #####################################
    #          Path Generation          #
    #####################################

    def constructRoad(self, length):
        grid = []
        even = False

        if length % 2 == 0:
            even = True

        while True:
            top = random.randrange(self.cols - 1)
            bot = random.randrange(self.cols - 1)

            # if the number of tiles that needs to be traveled isn't the same odd/even as the distance,
            # a path will not be able to be generated, cause math
            if (top + bot + self.rows-1) % 2 == even:
                break

        start = (top, 0)
        end = (bot, self.rows - 1)

        for i in range(0, self.cols):
            grid.append([])
            for j in range(0, self.rows):
                grid[i].append(0)

        path = self.generatePath(grid, start, end, length)

        for i in range(0, self.cols):
            for j in range(0, self.rows):
                if path[i][j] == 1:
                    self.grid[i][j] = tileFactory.getTile("road", self.x + self.tileSize * i, self.y + self.tileSize * j, self.tileSize)

        index = (start[0], start[1])
        self.grid[index[0]][index[1]].entry = Dir.NORTH
        self.grid[end[0]][end[1]].exit = Dir.SOUTH
        while index != end:
            path[index[0]][index[1]] = -1
            # North if able
            if index[1] != 0:
                if path[index[0]][index[1]-1] > 0:
                    self.grid[index[0]][index[1]].exit = Dir.NORTH
                    self.grid[index[0]][index[1]-1].entry = Dir.SOUTH
                    index = (index[0], index[1]-1)
                    continue

            # West if able
            if index[0] != 0:
                if path[index[0]-1][index[1]] > 0:
                    self.grid[index[0]][index[1]].exit = Dir.WEST
                    self.grid[index[0]-1][index[1]].entry = Dir.EAST
                    index = (index[0]-1, index[1])
                    continue

            # South if able
            if index[1] != self.rows - 1:
                if path[index[0]][index[1] + 1] > 0:
                    self.grid[index[0]][index[1]].exit = Dir.SOUTH
                    self.grid[index[0]][index[1] + 1].entry = Dir.NORTH
                    index = (index[0], index[1] + 1)
                    continue

            # East if able
            if index[0] != self.cols - 1:
                if path[index[0] + 1][index[1]] > 0:
                    self.grid[index[0]][index[1]].exit = Dir.EAST
                    self.grid[index[0] + 1][index[1]].entry = Dir.WEST
                    index = (index[0] + 1, index[1])
                    continue

        self.start = start

    def generatePath(self, grid, start, end, length):

        # if been here before
        if grid[start[0]][start[1]] == 1:
            return grid

        # if touches any tile other than previous
        if self.getNumGridNeighbors(grid, start) > 1:
            return grid

        grid[start[0]][start[1]] = 1
        length = length - 1
        dirs = [0, 1, 2, 3]

        # if at the end
        if start == end:
            # if desired length
            if length == 0:
                return grid
            grid[start[0]][start[1]] = 0
            return grid

        # if exhausted length allowance
        if length == 0:
            grid[start[0]][start[1]] = 0
            return grid

        while len(dirs) != 0:
            dirToGo = dirs[random.randrange(len(dirs))]
            dirs.remove(dirToGo)

            # Recurse North if able
            if dirToGo == 0 and start[1] != 0:
                self.generatePath(grid, (start[0], start[1] - 1), end, length)

            # Recurse West if able
            if dirToGo == 1 and start[0] != 0:
                self.generatePath(grid, (start[0] - 1, start[1]), end, length)

            # Recurse South if able
            if dirToGo == 2 and start[1] != self.rows - 1:
                self.generatePath(grid, (start[0], start[1] + 1), end, length)

            # Recurse East if able
            if dirToGo == 3 and start[0] != self.cols - 1:
                self.generatePath(grid, (start[0] + 1, start[1]), end, length)

            if grid[end[0]][end[1]] == 1:
                return grid

        grid[start[0]][start[1]] = 0
        return grid

    def getNumGridNeighbors(self, grid, point):
        count = 0

        if point[0] != 0:
            if grid[point[0] - 1][point[1]] == 1:
                count += 1

        if point[0] != self.cols - 1:
            if grid[point[0] + 1][point[1]] == 1:
                count += 1

        if point[1] != 0:
            if grid[point[0]][point[1] - 1] == 1:
                count += 1

        if point[1] != self.rows - 1:
            if grid[point[0]][point[1] + 1] == 1:
                count += 1

        return count
