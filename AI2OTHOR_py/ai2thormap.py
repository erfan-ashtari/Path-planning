# -*- coding: utf-8 -*-
"""AI2THOR-map.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1decj39QzG3kS5HBRD1VqHiDOiGL2ayB4
"""

map_name=-1
while map_name<0 or map_name>194:
  map_name = input("which map? [choose a number between 0 and 194] : ")
  try:
    map_name = int(map_name)
  except:
    map_name=-1
    print("[insert a number!]")

data = []
data.append(str(map_name))


# FloorPlan227_physics = 56
# FloorPlan203_physics = 32

from google.colab import drive
drive.mount('/content/drive')

"""#AI2THOR map

## Installation

⚡ _Note_: AI2-THOR often runs significantly _slower_ using Colab's runtime than it does with a local runtime. However, in many cases, it is nice to explore without installing anything locally and not all devices are compatible with running AI2-THOR (e.g., Windows devices, tablets, phones).
"""

#pip install --upgrade ai2thor ai2thor-colab &> /dev/null
import ai2thor
import ai2thor_colab

from ai2thor.controller import Controller
from ai2thor_colab import (
    plot_frames,
    show_objects_table,
    side_by_side,
    overlay,
    show_video
)

ai2thor_colab.start_xserver()

"AI2-THOR Version: " + ai2thor.__version__

import random
from math import cos, sin, atan2
import matplotlib.path as mplPath
import time
import collections
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from multiprocessing import Pool
import tensorflow as tf
import shapely.geometry
import descartes
from shapely import geometry
import numpy.matlib as mat
from tqdm import tqdm
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, LSTM
from keras import optimizers
from keras.callbacks import LearningRateScheduler
import keras
from keras.layers import Dropout
from keras import backend as K
from tensorflow.python.keras.utils import metrics_utils 
from tensorflow.python.ops import math_ops 
from tensorflow.python.framework import ops
# from google.colab import drive
# drive.mount('/content/drive')

import os

main_directory = os.getcwd()
print("directory =",main_directory )

# checking if the directory demo_folder2
# exist or not.
if not "ai2thor_files" in main_directory : 
    if not os.path.isdir("ai2thor_files"):        
        # if the demo_folder2 directory is
        # not present then create it.
        os.makedirs(main_directory+"/ai2thor_files")
    os.chdir("ai2thor_files")

main_directory = os.getcwd()

print("directory =",main_directory )

map_name = Controller().scene_names()[map_name]

map_name

controller = Controller(scene = map_name)

size_x = controller.last_event.metadata['sceneBounds']["size"]["x"]
size_z = controller.last_event.metadata['sceneBounds']["size"]["z"]

cam_x = 800
cam_z = (size_z/size_x) * cam_x

X = np.array(controller.last_event.metadata['sceneBounds']["cornerPoints"])[:,0]
Z = np.array(controller.last_event.metadata['sceneBounds']["cornerPoints"])[:,2]
Y = np.array(controller.last_event.metadata['sceneBounds']["cornerPoints"])[:,1]

agent_x = controller.last_event.metadata["agent"]["position"]["x"]
agent_z = controller.last_event.metadata["agent"]["position"]["z"]
agent_y = controller.last_event.metadata["agent"]["position"]["y"]

# map_name = controller.scene_names()[map_name]
# map_name = 'FloorPlan226_physics'
controller = Controller(scene=map_name,gridSize=0.005)

"""## Comparison to starting `GetReachablePositions`"""

starting_positions = controller.step(action="GetReachablePositions").metadata["actionReturn"]
starting_positions

import matplotlib.pyplot as plt


# def fig2data ( fig ):
#    # """
#    # @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
#    # @param fig a matplotlib figure
#    # @return a numpy 3D array of RGBA values
    # """
#     # draw the renderer
#     fig.canvas.draw ( )
 
#     # Get the RGBA buffer from the figure
#     w,h = fig.canvas.get_width_height()
#     buf = np.fromstring ( fig.canvas.tostring_argb(), dtype=np.uint8 )
#     buf.shape = ( w, h,4 )
 
#     # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
#     buf = np.roll ( buf, 3, axis = 2 )
#     return buf

# plt.xlim(OUTER_x.min(),OUTER_x.max())
# plt.ylim(OUTER_z.min(),OUTER_z.max())

def plot_positions(positions, FIGSIZE = (1,1) , size=1 , color="k" ,X_=None, Z_=None, OUTER_X=None, OUTER_Z=None , save_name= None):
    xs = [p["x"] for p in positions]
    zs = [p["z"] for p in positions]
    fig = plt.figure(figsize= FIGSIZE )
    fig.set_facecolor("black")
    ax = fig.add_subplot(111)
    plt.scatter(xs, zs, s= size ,c = color )
    # ax.scatter(xs, zs,c="white")
    ax.axis('off')
    # print(type(X_))
    if X_ is not None and Z_ is not None :
      plt.xticks(np.arange(X_.min(), X_.max(), 0.2))
      plt.yticks(np.arange(Z_.min(), Z_.max(), 0.1))
    if OUTER_X is not None and OUTER_Z is not None :
      plt.xlim(OUTER_X.min(),OUTER_X.max())
      plt.ylim(OUTER_Z.min(),OUTER_Z.max())
    # fig = plt.gcf()
    # fig.savefig("1.png" , bbox_inches='tight', pad_inches=0)    
    if save_name != None:
      fig.savefig(save_name+".pdf",format="pdf", bbox_inches='tight', pad_inches=0,facecolor="black")
      fig.savefig(save_name+".png" , bbox_inches='tight', pad_inches=0,facecolor="black") 
    # npdata = fig2data ( fig ) 
    # print(npdata) 

    # plt.xlabel("x")
    # plt.ylabel("z")

# plot_positions(starting_positions , FIGSIZE = (2,2),color = "green", save_name =map_name )

reachable_x = []
reachable_z = []
reachable_y = []

for a in starting_positions:
  reachable_x.append( a["x"] )
  reachable_y.append( a["y"] )
  reachable_z.append( a["z"] )

reachable_x = np.array(reachable_x)
reachable_y = np.array(reachable_y)
reachable_z = np.array(reachable_z)

print("x: ",reachable_x.max() , reachable_x.min())
print("z: ",reachable_z.max() , reachable_z.min())



OUTER_x = np.array([X[0], X[1], X[-1], X[-2] , X[0] ])
OUTER_z = np.array([ Z[0], Z[1], Z[-1], Z[-2] ,Z[0] ])

inner_x = np.array([ reachable_x.max() , reachable_x.max() , reachable_x.min() , reachable_x.min() ,reachable_x.max() ] )
inner_z = np.array([ reachable_z.max() , reachable_z.min() , reachable_z.min() , reachable_z.max() , reachable_z.max() ] )

(cam_z/cam_x)

plot_positions(starting_positions , FIGSIZE = ( 10 , (cam_z/cam_x)*10  ) ,color = "white", OUTER_X=OUTER_x, OUTER_Z = OUTER_z, save_name =map_name )
# plt.plot( inner_x , inner_z , linewidth = 3 , color="blue")
# plt.plot( OUTER_x , OUTER_z , linewidth = 1, color="red",)
# plt.xlim(OUTER_x.min()-.01,OUTER_x.max()+.01)
# plt.ylim(OUTER_z.min()-.01,OUTER_z.max()+.01)

"""## 1. Hide the Objects"""

hidden_objects = []
for obj in controller.last_event.metadata["objects"]:
    if obj["objectType"] not in {"Floor"}:
        hidden_objects.append(obj["objectId"])
        controller.step(
            action="DisableObject",
            objectId=obj["objectId"]
        )

"""## 2. Get the reachable positions after disabling the objects"""

ending_positions = controller.step(action="GetReachablePositions").metadata["actionReturn"]
plot_positions(ending_positions)

"""## 3. Re-Enable the objects"""

for object_id in hidden_objects:
    controller.step(
        action="EnableObject",
        objectId=object_id
    )

assert len(controller.last_event.metadata["objects"]) > 1, "Num Objects should be > 1"

# im =plt.imread(map_name+"_100points.png")

# # plt.axis="off"
# plt.imshow(im)

"""# generate map

## resize map
"""

from PIL import Image

basewidth = 350
img = Image.open(map_name+".png")
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
print(hsize)
img = img.resize((basewidth,hsize), Image.ANTIALIAS)
map_name_resized = map_name+"_resized"
img.save(map_name_resized+'.png')


# img = Image.open('/content/drive/My Drive/AI2THOR/map/FloorPlan227.png')

# new_width  = 200
# new_height = 300
# img = img.resize((new_width, new_height), Image.ANTIALIAS)

# img.save('/content/drive/My Drive/oraclenet-analysis-master/taarlab/map/resize_taarlab_map4.jpg')

"""##corner detection"""

import cv2
import numpy as np
from google.colab.patches import cv2_imshow

# Load the image
img = cv2.imread(map_name_resized+'.png')
# Convert to greyscale
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Convert to binary image by thresholding
_, threshold = cv2.threshold(img_gray, 220, 200, cv2.THRESH_BINARY_INV)
# Find the contours
contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# For each contour approximate the curve and
# detect the shapes.
p = []
for cnt in contours:
    epsilon = 0.001*cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    cv2.drawContours(img, [approx], 0, (0), 1)
    # Position for writing text
    # x,y = approx[0][0]

    if(len(approx) >= 4): 
      if(len(approx) < 300):
        p.append(approx)
 
        cv2.drawContours(img, [approx], 0, (0, 0, 255), 1) 
 
cv2_imshow(img)

for i in range(len(p)):
  img = cv2.imread(map_name_resized+'.png')
  # Convert to greyscale
  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  p[i] = p[i].reshape(-1,2)[::-1]

  cv2.drawContours(img, [p[i]], 0, (255, 0, 0), 2)
  cv2_imshow(img)
  print(i)

"""##merge contours"""

# print("before p[0] :",p[0].shape)
# print("before p[1] :",p[1].shape)


# p0=p[0]
# p01 = p0.tolist()
# # p01 = p0[::-1].tolist()

# p01.append(p01[0])
# p01 = np.array(p01)
# p01 = p01[::-1]
# p02 = p01.tolist()

# # p1 = p[1].tolist()
# p1 = p[1][::-1].tolist()

# p1.append(p1[0])
# for x in p1 :
#   p02.append(x)

# p02= np.array(p02)

# print("after combined : ",p02.shape)



# print("before p[0] :",p[0].shape)
# print("before p[1] :",p[1].shape)


# print("before p[0] :",p[0].shape)
# print("before p[1] :",p[1].shape)


# p0=p[0]
# p01 = p0.tolist()
# p01.append(p01[0])
# p01 = np.array(p01)

# p1=p[1]
# p11 = p1.tolist()
# p11.append(p11[0])
# p11 = np.array(p11)

# print("before p[0] :",p01.shape)
# print("before p[1] :",p11.shape)
# p02 = p01.tolist()


# p1 = p[1].tolist()

# p1.append(p1[0])
# for x in p1 :
#   p02.append(x)

# p02= np.array(p02)

# print("after combined : ",p02.shape)

print("before p[0] :",p[0].shape)
print("before p[1] :",p[1].shape)


p0=p[0]
p01 = p0.tolist()
p01.append(p01[0])
p01 = np.array(p01)

p1=p[1]
p11 = p1.tolist()
rights = np.where( np.array(p11)[:,0] == np.array(p11)[:,0].max() )[0]

if len(rights)>1:
  for i,t in enumerate(rights):
    # print(i)
    # print(t)
    # print( np.array(p11)[t,1] )

    if i ==0:
      temp = np.array(p11)[t,1]
    else:
      if np.array(p11)[t,1] < temp:
        temp = np.array(p11)[t,1]
    # print("=====")
  # print(temp)
  # print( np.array( [ np.array(p11)[:,0].max() , temp ] ) )
  arg_point = (np.array(p11) == np.array( [ np.array(p11)[:,0].max() , temp ] )).sum(1).argmax()
  # print(arg_point)
  point = p11[arg_point]
else:
  arg_point = rights[0]
  point = p11[arg_point]

# print( p11[arg_point: ]+ p11[ : arg_point ] )
p11 = p11[arg_point: ]+ p11[ : arg_point ]
# print(np.where( np.array(p11)[:,0] == np.array(p11)[:,0].max() ) )
p11.append(p11[0])
p11 = np.array(p11)
# print(p11)
print("after p[0] :",p01.shape)
print("after p[1] :",p11.shape)
p02 = p01.tolist()


for x in p11 :
  p02.append(x)

p02= np.array(p02)

print("after combined : ",p02.shape)

# p_ext = np.array( [ [p01[0][0],p01[0][1]] , [p01[1][0],p01[1][1]] ,[p11[-1][0],p01[1][1]] , [p11[-1][0],p01[0][1]] ] )

print("before : ")
# p = p[i].reshape(-1,2)[::-1]
img = cv2.imread(map_name_resized+'.png')
cv2.drawContours(img, [ p[0] ], 0, (255, 0, 0), 2)
# cv2_imshow(img)

# img = cv2.imread('/content/drive/My Drive/AI2THOR/map/FloorPlan227.png')
cv2.drawContours(img, [ p[1] ], 0, (255, 0, 0), 2)
cv2_imshow(img)
print("\n")
print("after : ")

img = cv2.imread(map_name_resized+'.png')
cv2.drawContours(img, [ p02 ], 0, (255, 0, 0), 2)
cv2_imshow(img)

p = p[2:]
p.append(p02)
p

# s = np.array( [ [p01[-1][0],p01[-1][1]] , [p01[-1][0],p11[-1][1]] ,[p11[-1][0],p11[-1][1]] , [p11[-1][0],p01[-1][1]] ] )
s = np.array( [ [p01[0][0],p01[0][1]] , [p01[1][0],p01[1][1]] ,[p11[-1][0],p01[1][1]] , [p11[-1][0],p01[0][1]] ] )

p.append(s)

"""## CW & CCW"""

CW = []
for i in range(len(p)):
  C = 0
  for j in range(len(p[i])-1):
    c = (p[i][j+1][0]-p[i][j][0])*(p[i][j+1][1]+p[i][j][1])
    C += c
  CW.append(C)
print(p)

final_final = []
for i,k in enumerate(CW):
  if k > 0:
    for f in p[i:i+1]:
      final_final.append(f[::-1].tolist())
  if k < 0:
    for f in p[i:i+1]:
      final_final.append(f.tolist())
final_final

CW

"""## remove points close together"""

def distance(pt1, pt2):
    (x1, y1), (x2, y2) = pt1, pt2
    dist = np.math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
    return dist

P_COPY = []

for P in final_final:
  p_copy = []
  p_copy.append(P[0])

  for i in range(len(P)-1):
    if distance(P[i],P[i+1]) > 2:
      p_copy.append(P[i+1])
  P_COPY.append(np.array(p_copy))

for i in range(len(P_COPY)):
  img = cv2.imread(map_name_resized+'.png')
  # Convert to greyscale
  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  cv2.drawContours(img, [np.array(P_COPY[i])], 0, (255, 0, 0), 2)
  cv2_imshow(img)
  print(i)

"""##save map"""

np.save(map_name_resized+'_wo.npy',np.array(P_COPY), allow_pickle=True)

print(img.shape)

imgshape = (img.shape[1] , img.shape[0])
# imgshape = (500,235)

# data = []
data.append(map_name_resized)


data.append(str(imgshape[0]))
data.append(str(imgshape[1]))

file = open('items.txt','w')
for item in data:
	file.write(item+"\n")
file.close()