from Tiles.tile import Tile
from grid import Grid
from GUI.menu import Menu
from GUI.controlBar import ControlBar, ControlAction
from GUI.selectedItemDisplay import SelectedItemDisplay
import pygame
import sys
import math
import copy
import globals


def preventSpill(screen):
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, tileGrid.x - tileGrid.borderWidth, tileGrid.y + tileGrid.tileSize * tileGrid.rows + tileGrid.borderWidth))
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, tileGrid.x + tileGrid.tileSize * tileGrid.cols + tileGrid.borderWidth, tileGrid.x - tileGrid.borderWidth))
    pygame.draw.rect(screen, (255, 255, 255), (tileGrid.x + tileGrid.tileSize * tileGrid.cols + tileGrid.borderWidth, 0, globals.windowWidth, globals.windowHeight))
    pygame.draw.rect(screen, (255, 255, 255), (0, tileGrid.y + tileGrid.tileSize * tileGrid.rows + tileGrid.borderWidth, globals.windowWidth, globals.windowHeight))

pygame.init()
screen = pygame.display.set_mode((globals.windowWidth, globals.windowHeight))
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250))

screen.blit(background, (0, 0))
pygame.display.flip()
pygame.display.set_caption('Color Guard')
icon = pygame.image.load('resources/colorGuardIcon.png')
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

holdingTile = False
heldTile = Tile(0, 0, 0)
selectedTile = heldTile
tileGrid = Grid((15, 15), (7, 11), 40)
itemMenu = Menu((15, 350), (100, 100), 470)
controlBar = ControlBar((15, 310))
selectedItemDisplay = SelectedItemDisplay((10,110))

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if not holdingTile:
                if selectedTile is not None:
                    selectedTile.selected = False
                    selectedTile = None
                if itemMenu.isInMenu(pos):
                    heldTile = itemMenu.getItem(pos)
                    pygame.mouse.set_visible(0)
                    heldTile.selected = True
                    holdingTile = True
                    tileGrid.showLines(True)
                elif tileGrid.isInGrid(pos):
                    selectedTile = tileGrid.getTileAtPos(pos)
                    selectedTile.selected = True
                else:
                    action = controlBar.getAction(pos)
                    if action == ControlAction.START:
                        tileGrid.startWave()
                    elif action == ControlAction.RESET:
                        tileGrid.regenerateGrid()
                        selectedTile = None

            else:
                if tileGrid.isInGrid(pos):
                    if tileGrid.isPlaceableAtPos(pos):
                        tile = copy.deepcopy(heldTile)
                        selectedTile = tile
                        tileGrid.setTileAtPos(pos, tile)
                        heldTile.selected = False
                        heldTile = Tile(0, 0, 0)
                    else:
                        break
                elif itemMenu.isInMenu(pos):
                    heldTile = itemMenu.getItem(pos)
                    heldTile.selected = True
                    break
                else:
                    heldTile = Tile(0, 0, 0)
                pygame.mouse.set_visible(1)
                holdingTile = False
                tileGrid.showLines(False)

    if holdingTile:
        pos = pygame.mouse.get_pos()
        if tileGrid.isPlaceableAtPos(pos):
            heldTile.isGreyed = False
        else:
            heldTile.isGreyed = True
        x = pos[0] - math.floor(heldTile.size / 2)
        y = pos[1] - math.floor(heldTile.size / 2)
        heldTile.updatePos((x, y))

    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))

    tileGrid.update()
    tileGrid.draw(screen)
    if selectedTile is not None:
        selectedTile.draw(screen)
    preventSpill(screen)
    itemMenu.draw(screen)
    controlBar.draw(screen)
    heldTile.draw(screen)
    pygame.display.flip()
