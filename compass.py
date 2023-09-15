# calculate the azimuth of the normal vector which is orthgonal to two GPS points
# we assume that the earth is plane; it make sense because the two GPS points are so close (< 1 m) enough to ignore the curvature of the earth
# if you assume that the earth is sphere, refer to here: https://spiralmoon.tistory.com/entry/Algorithm-%EC%A7%80%EA%B5%AC%EC%97%90%EC%84%9C-%EB%91%90-%EC%A0%90-%EC%82%AC%EC%9D%B4%EC%9D%98-%EB%B0%A9%EC%9C%84%EA%B0%81-%EA%B5%AC%ED%95%98%EA%B8%B0

import numpy as np
import math
from matplotlib import pyplot as plt
import argparse
from haversine import haversine

# x means longitude, y means laptitude 
x1 = 127.1614; y1 = 37.4033
x2 = 127.1615; y2 = 37.4030

dx=x2-x1; dy = y2-y1
angle =  math.atan(dy/dx)*(180/math.pi)

# for counter-clockwise
if dx<0.0:
    angle += 180
else:
    if dy<0.0:
        angle += 360
        
# for clockwise
angle = 360-angle

# calculate normal
nor_angle = angle + 90
if nor_angle>360:
    nor_angle -= 360

# calculate the distance 
dist = haversine([y1,x1],[y2,x2], unit = 'm') # laptitude, longitude

plt.figure(figsize=(8,8))
plt.plot((x1,x2),(y1,y2),'b-s')
plt.title('angle:'+f"{angle:.1f}"+' ° '+' normal:'+f"{nor_angle:.1f}"+' ° '+' distance: ' + f"{dist:.1f}"+' m')
plt.text(x1,y1,'s')
plt.text(x2,y2,'e')
plt.show()