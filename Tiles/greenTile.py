from Tiles import towerTile
import pygame


class GreenTile(towerTile.TowerTile):
    name = "green"
    isTower = True
    color = (0, 255, 0)
    greyColor = (0, 100, 0)
    radius = 200
    damage = 80
    fireRate = 2

    def __init__(self, x, y, size):
        towerTile.TowerTile.__init__(self, x, y, size)