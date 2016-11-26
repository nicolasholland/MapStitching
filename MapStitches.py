import os
import requests
import cv2
from matplotlib import pyplot as plt
import numpy as np

LAT = 48.8566
LON = 2.3522

ZOOM = 16

# Size if tiles
mapTileX = 1280
mapTileY = 1280

# Variables that store how many tiles are used for stitching
nofMapTilesX = 3
nofMapTilesY = 3

# Variables to keep track of coordinates in the global coord system
globalStartX = 0
globalStartY = 0

# Folders
path = "tmp"
outpath = "output"

# PatchSize is: patchR X patchR
patchR = 5

# Variable is set to True whenever a new row is started to get stitched
StitchOnY = False

# THESE DEPEND ON THE ZOOM
moveX = 0.0135
moveY = -0.0085

# Create empty canvas for tiles
eX = nofMapTilesX * mapTileX
eY = nofMapTilesY * mapTileY

empty = np.zeros((eX, eY, 3), np.uint8)

Y = 0
def GetPatch(x,y,r,A):
  empty = np.zeros((2*r, 2*r, 3), np.uint8)

  for i in range(0,2*r):
    for j in range(0,2*r):
      for c in range(0, 3):
        empty[i][j][c] = A[y - r + i][x - r + j][c]

  return empty

def ComparePatch(P1, P2, r):
  total = 0
  for i in range(0,2*r):
    for j in range(0,2*r):
      for c in range(0, 3):
        total += abs(P1[i][j][c]*1.0 - P2[i][j][c]*1.0)
  return total

def SearchMatchH(Patch1, mapTile, patchR):
  mintot = 9999
  minsX = 0
  minsY = 0

  # restrict the area in which the patch is searched in
  for sX in range(4,7):
    for sY in range(265,280):    
      Patch2 = GetPatch(sX, sY, patchR, mapTile)
      tot = ComparePatch(Patch1, Patch2, patchR)
  
      if tot < mintot:
        mintot = tot
        minsX = sX
        minsY = sY

  return sX, sY

def SearchMatchV(Patch1, mapTile, patchR):
  mintot = 9999
  minsX = 0
  minsY = 0

  # restrict the area in which the patch is searched in
  for sX in range(1020,1030):
    for sY in range(5,40):
      Patch2 = GetPatch(sX, sY, patchR, mapTile)

      tot = ComparePatch(Patch1, Patch2, patchR)

      if tot < mintot:
        mintot = tot
        minsX = sX
        minsY = sY

  return sX, sY

end = False
StitchOnY = False
progress = 1
progressTotal = nofMapTilesX * nofMapTilesY
for tY in range(0, nofMapTilesY):
  for tX in range(0, nofMapTilesX):
    # get Coords
    lon = LON - int(nofMapTilesX/2) * moveX + tX * moveX
    lat = LAT - int(nofMapTilesY/2) * moveY + tY * moveY

    # get Map
    print "Downloading " + str(progress) + "/" + str(progressTotal)
    f=open(path+'/'+str(tX)+str(tY)+'.png','wb')
    f.write(requests.get("http://maps.googleapis.com/maps/api/staticmap?center=%f,%f&zoom=%d&size=640x640&scale=2&maptype=hybrid&language=en-EN&sensor=false"%(lat,lon,ZOOM)).content)
    f.close()
    
    # get MapTile
    mapTile = cv2.imread(path+'/'+str(tX)+str(tY)+'.png')
    b,g,r   = cv2.split(mapTile)
    mapTile = cv2.merge((r,g,b))

    # First Tile just gets in the image
    if tX == 0 and tY == 0:
      for x in range(globalStartX, globalStartX + mapTileX):
        for y in range(globalStartY, globalStartY + mapTileY):
          for c in range(0, 3):
            empty[y][x][c] = mapTile[y % mapTileY][x % mapTileX][c]
      oldMapTile = mapTile
      globalStartX = globalStartX + mapTileX
      cY = 0
      progress = progress + 1
      continue

    print "Stitching " + str(progress) + "/" + str(progressTotal)
    if StitchOnY:
      cX = 0
  
      # Read OldMapTile
      oldMapTile = cv2.imread(path+'/'+str(tX)+str(tY-1)+'.png')
      b,g,r      = cv2.split(oldMapTile)
      oldMapTile = cv2.merge((r,g,b))

      # look for patches for vertical stitches
      Patch1 = GetPatch(1025, 1215, patchR, oldMapTile)

      # look in the lower/upper right corner for a match    
      vX, vY = SearchMatchV(Patch1, mapTile, patchR)

      # transform vX,vY from the patch coordsystem into global System and compute correction
      cY = abs((tY-1)*mapTileY+1215 - (tY * mapTileY + vY))
      #cY = cY -2
      print cY

    else:
      # Patch finding
      Patch1 = GetPatch(1265, 270, patchR, oldMapTile)

      # look in the upper right/left corner for a match    
      vX, vY = SearchMatchH(Patch1, mapTile, patchR)
        
      # transform vX,vY from the patch coordsystem into global System and compute correction
      cX = abs((tX-1)*mapTileX+1265 - (tX * mapTileX + vX))

    # Put Together
    localX = 0
    for x in range(globalStartX, globalStartX + mapTileX):
      localY = 0
      for y in range(globalStartY, globalStartY + mapTileY):
        for c in range(0, 3):
          empty[y - cY][x - cX][c] = mapTile[localY % mapTileY][localX % mapTileX][c]
        localY += 1
      localX += 1
        

    oldMapTile = mapTile
    globalStartX = globalStartX + mapTileX - cX
    finalEndX = globalStartX
    StitchOnY = False
    progress = progress + 1

  StitchOnY = True
  globalStartX = 0
  globalStartY = globalStartY + mapTileY - cY


# Create empty canvas for tiles
output = np.zeros((globalStartY, finalEndX, 3), np.uint8)
print "Final adjustments "

for x in range(0, finalEndX):
  for y in range(0, globalStartY):
    for c in range(0, 3):
      output[y][x][c] = empty[y][x][c]

#plt.imshow(output)
#plt.show()

r,g,b  = cv2.split(output)
output = cv2.merge((b,g,r))

cv2.imwrite( outpath + '/' + str(LAT) + str(LON) + '.png',output)




  
