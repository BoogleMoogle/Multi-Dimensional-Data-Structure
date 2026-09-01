import numpy as np
import pandas as pd
import random


class DAGTree:
    def __init__(self, points=[], depth=0, axis=0, split_value=None, bbox=[], left=None, right=None, middle=None, middle_child=False, parent=[], cutoff=1):
        self.left = left
        self.right = right
        self.middle = middle
        self.parent = parent
        self.data_size = len(points)
        self.middle_child = middle_child
        self.cutoff = cutoff
        self.depth = depth
        self.axis = axis
        self.split_value = split_value

        if axis == 0:   #sorts by x values
            points.sort()
        else:           #sorts by y values
            points.sort(key=lambda x: x[1])
        self.points = points

        #set bbox (mainly used at the first creation of DAGTree)
        if len(bbox) == 0:
            self.bbox = self.find_bbox(bbox)
        else:
            self.bbox = bbox

        # if self.data_size > self.cutoff:
            # self.split()
        if self.parent == []:
            self.split()


    #To String Method
    def __str__(self):
        if self.split_value != None:
            if self.axis == 0:
                return f"Split Node: x = {self.split_value[self.axis]}, Level: {self.depth}, BBOX: {self.bbox}"#, Left: {self.left}, Right: {self.right}"
            else:
                return f"Split Node: y = {self.split_value[self.axis]}, Level: {self.depth}, BBOX: {self.bbox}"#, Left: {self.left}, Right: {self.right}"
        else:
            return f"{self.points}"



    #BBOX Method
    def find_bbox(self,bbox):
        for item in self.points:
            if len(bbox) == 0:
                bbox=[item[0], item[1], item[0], item[1]]
                #this sets the x min and max as the first x value and the same for the y min and max
            if bbox[0] > item[0]:       #xmin
                bbox[0] = item[0]
            if bbox[1] > item[1]:       #ymin
                bbox[1] = item[1]
            if bbox[2] <= item[0]:       #xmax
                bbox[2] = item[0]+1 #add 1 for [) type notation    
            if bbox[3] <= item[1]:       #ymax
                bbox[3] = item[1]+1 #add 1 for [) type notation   
        return bbox



    #Splitting Method
    def split(self):
        #sort points based on next level
        if self.axis == 0:  #x axis
            self.points.sort()
        else:
            self.points.sort(key=lambda x: x[1])


        # print(f"Mid Axis on axis {self.axis}: {self.points[(len(self.points)//2)][self.axis]}")   #-1 to be left heavy
        self.split_value = self.points[(len(self.points)//2)]   #this gives the split axis

        #Split data points into the left and right children
        right, left, middle = [], [], []
        for item in self.points:
            if item[self.axis] < self.split_value[self.axis]:       #if point (of axis) is less than split value, go left
                left.append(item)
            else:                                                   #if point (of axis) is greater than or equal to split value, go right
                right.append(item)

        # #Splitting points for middle child
        # print(f"Left: {left}")
        # print(f"Right: {right}")
        # print(f"Depth: {self.depth}")

                
        #need to check if all data points are going to one side, if so we need to stop
        if len(left) == 0 or len(right) == 0:
            return

        left_median = left[(len(left)//2)]  #median will always round up
        right_median = right[(len(right)//2)]   #median will always round up
        # print(f"Left Median: {left_median}\nRight Median: {right_median}")

        for item in self.points:
            if item[self.axis] >= left_median[self.axis] and item[self.axis] < right_median[self.axis]:
                middle.append(item)
        #need to check if middle bbox ends up equalling the right or the left childs bbox
        # print(f"Middle: {middle}\n")

        #Making the children
        if self.axis == 0:  #x axis
            i=0
            for item in left:
                if item[self.axis] != left[0][self.axis]:
                    break
                else:
                    i+=1
                    if i == len(left)-1:   #checking if every number in points list is on the same axis, if so we must stop
                        return
            self.left = DAGTree(left, depth=self.depth+1, axis=1, bbox=[self.bbox[0], self.bbox[1], self.split_value[self.axis], self.bbox[3]], parent=[self], cutoff=self.cutoff, middle_child=self.middle_child)

            i=0
            for item in right:
                if item[self.axis] != right[0][self.axis]:
                    break
                else:
                    i+=1
                    if i == len(right)-1:   #checking if every number in points list is on the same axis, if so we must stop
                        return
            self.right = DAGTree(right, depth=self.depth+1, axis=1, bbox=[self.split_value[self.axis], self.bbox[1], self.bbox[2], self.bbox[3]], parent=[self], cutoff=self.cutoff, middle_child=self.middle_child)

            i=0
            for item in middle:
                if item[self.axis] != middle[0][self.axis]:
                    break
                else:
                    i+=1
                    if i == len(middle)-1:   #checking if every number in points list is on the same axis, if so we must stop
                        return
            self.middle = DAGTree(middle, depth=self.depth+1, axis=1, bbox=[left_median[self.axis], self.bbox[1], right_median[self.axis], self.bbox[3]], parent=[self], middle_child=True, cutoff=self.cutoff)
        else:               #y axis
            i=0
            for item in left:
                if item[self.axis] != left[0][self.axis]:
                    break
                else:
                    i+=1
                    if i == len(left)-1:   #checking if every number in points list is on the same axis, if so we must stop
                        return
            self.left = DAGTree(left, depth=self.depth+1, axis=0, bbox=[self.bbox[0], self.bbox[1], self.bbox[2], self.split_value[self.axis]], parent=[self], cutoff=self.cutoff, middle_child=self.middle_child)

            i=0
            for item in right:
                if item[self.axis] != right[0][self.axis]:
                    break
                else:
                    i+=1
                    if i == len(right)-1:   #checking if every number in points list is on the same axis, if so we must stop
                        return
            self.right = DAGTree(right, depth=self.depth+1, axis=0, bbox=[self.bbox[0],self.split_value[self.axis],self.bbox[2],self.bbox[3]], parent=[self], cutoff=self.cutoff, middle_child=self.middle_child)

            i=0
            for item in middle:
                if item[self.axis] != middle[0][self.axis]:
                    break
                else:
                    i+=1
                    if i == len(middle)-1:   #checking if every number in points list is on the same axis, if so we must stop
                        return
            self.middle = DAGTree(middle, depth=self.depth+1, axis=0, bbox=[self.bbox[0],left_median[self.axis],self.bbox[2],right_median[self.axis]], parent=[self], middle_child=True, cutoff=self.cutoff)

        self.points=None

        if self.left.data_size > self.cutoff:
            # print("Going Left")
            self.left.split()
        if self.middle.data_size > self.cutoff:
            # print("Going Middle")
            self.middle.split()
        if self.right.data_size > self.cutoff:
            # print("Going Right")
            self.right.split()



    #SRC, middle
    def SRC_middle(self, q_xmin, q_ymin, q_xmax, q_ymax, inc_num_hops=False, num_hops=0):
        if self.middle != None:
            if self.middle.bbox[0] <= q_xmin and self.middle.bbox[2] >= q_xmax and self.middle.bbox[1] <= q_ymin and self.middle.bbox[3] >= q_ymax:     #we want to go down the middle first because it has the widest search
                return self.middle.SRC_middle(q_xmin, q_ymin, q_xmax, q_ymax, inc_num_hops, num_hops+1)

        if self.left != None:
            if self.left.bbox[2] >= q_xmax and self.left.bbox[3] >= q_ymax:
                return self.left.SRC_middle(q_xmin, q_ymin, q_xmax, q_ymax, inc_num_hops, num_hops+1)

        if self.right != None:
            if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                return self.right.SRC_middle(q_xmin, q_ymin, q_xmax, q_ymax, inc_num_hops, num_hops+1)
        if inc_num_hops == False:
            return self
        else:
            return [self, num_hops]



    #SRC, exhaustive
    def SRC_exhaustive(self, q_xmin, q_ymin, q_xmax, q_ymax, best=None):
        if self.bbox[0] >= q_xmin or self.bbox[1] >= q_ymin or self.bbox[2] <= q_xmax or self.bbox[3] <= q_ymax and (best != None and best.depth < self.depth):
            best = self

        if self.left != None and self.left.bbox[2] >= q_xmax and self.left.bbox[3] >= q_ymax:
            temp = self.left.SRC_exhaustive(q_xmin, q_ymin, q_xmax, q_ymax, best)
            if temp != None and (best == None or temp.depth > best.depth):
                best = temp

        if self.middle != None and self.middle.bbox[0] <= q_xmin and self.middle.bbox[2] >= q_xmax and self.middle.bbox[1] <= q_ymin and self.middle.bbox[3] >= q_ymax:
            temp = self.middle.SRC_exhaustive(q_xmin, q_ymin, q_xmax, q_ymax, best)
            if temp != None and (best == None or temp.depth > best.depth):
                best = temp

        if self.right != None and self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
            temp = self.right.SRC_exhaustive(q_xmin, q_ymin, q_xmax, q_ymax, best)
            if temp != None and (best == None or temp.depth > best.depth):
                best = temp
            
        return best



    #SRC, random
    def SRC_random(self, q_xmin, q_ymin, q_xmax, q_ymax, inc_num_hops=False, num_hops=0, seed=None):
        if seed != None:
            random.seed(seed)

        child_list = []

        if self.left != None:
            if self.left.bbox[2] >= q_xmax and self.left.bbox[3] >= q_ymax:
                child_list.append(self.left)

        if self.middle != None:
            if self.middle.bbox[0] <= q_xmin and self.middle.bbox[2] >= q_xmax and self.middle.bbox[1] <= q_ymin and self.middle.bbox[3] >= q_ymax:     #we want to go down the middle first because it has the widest search
                child_list.append(self.middle)

        if self.right != None:
            if self.right.bbox[0] <= q_xmin and self.right.bbox[1] <= q_ymin:
                child_list.append(self.right)

        if len(child_list) == 0:
            return self
        else:
            return child_list[random.randint(0,(len(child_list)-1))].SRC_random(q_xmin, q_ymin, q_xmax, q_ymax, inc_num_hops, num_hops+1, seed)



    def linear_BRC(self, q_xmin, q_ymin, q_xmax, q_ymax):
        #Only traverse right and left
        #Go as deep as possible for left and right
        #Return/Get all points
        nodes = self.get_leaf_linear(points_list=[], query=[q_xmin, q_ymin, q_xmax, q_ymax])
        return nodes



    def get_leaf_linear(self,points_list=[], query=[]):
        if self.points != None:
            for item in self.points:
                if item[0] >= query[0] and item[0] <= query[2] and item[1] >= query[1] and item[1] <= query[3]:
                    points_list.append(item)
        if self.left != None:
            self.left.get_leaf_linear(points_list, query)
        if self.right != None:
            self.right.get_leaf_linear(points_list, query)
        return points_list





#SRC, look to middle first
#Use synthetic data (uniform)
#For creating queries use corner method

points = []
for i in range(4):
    for j in range(4):
        points.append((i,j))

# print(f"# of points: {len(points)}")
tree = DAGTree(points, cutoff=4, axis=0)
print(f"Tree: {tree}")
# print(f"Left:\t{tree.left.bbox}\nMiddle:\t{tree.middle.bbox}\nRight:\t{tree.right.bbox}")
# print(f"Left Middle BBOX: {tree.left.middle.bbox}\nMiddle Middle BBOX: {tree.middle.middle.bbox}\nRight Middle BBOX: {tree.right.middle.bbox}")
# print(f"Middle Left: {tree.middle.left.bbox}\nMiddle Right: {tree.middle.right.bbox}")

# # print(f"SRC_middle []: {tree.SRC_middle(q_xmin=, q_ymin=, q_xmax=, q_ymax=)}")
# print(f"3DAG SRC_middle [1,2,2,3]: {tree.SRC_middle(q_xmin=1, q_ymin=2, q_xmax=2, q_ymax=3).bbox}")
# print(f"3DAG SRC_middle [0,0,0,0]: {tree.SRC_middle(q_xmin=0, q_ymin=0, q_xmax=0, q_ymax=0).bbox}")
# print(f"3DAG SRC_middle [4,4,4,4]: {tree.SRC_middle(q_xmin=4, q_ymin=4, q_xmax=4, q_ymax=4).bbox}")
# print(f"3DAG SRC_middle [1,1,2,2]: {tree.SRC_middle(q_xmin=1, q_ymin=1, q_xmax=2, q_ymax=2).bbox}")
# print("\n\n\n")

# # print(f"SRC_exhaustive []: {tree.SRC_exhaustive(q_xmin=, q_ymin=, q_xmax=, q_ymax=)}")
# print(f"SRC_exhaustive [1,2,2,3]: {tree.SRC_exhaustive(q_xmin=1, q_ymin=2, q_xmax=2, q_ymax=3).bbox}")
# print(f"SRC_exhaustive [0,0,0,0]: {tree.SRC_exhaustive(q_xmin=0, q_ymin=0, q_xmax=0, q_ymax=0).bbox}")
# print(f"SRC_exhaustive [4,4,4,4]: {tree.SRC_exhaustive(q_xmin=4, q_ymin=4, q_xmax=4, q_ymax=4).bbox}")
# print(f"SRC_exhaustive [1,1,2,2]: {tree.SRC_exhaustive(q_xmin=1, q_ymin=1, q_xmax=2, q_ymax=2).bbox}")
# print("\n\n\n")

# # print(f"SRC_random []: {tree.SRC_random(q_xmin=, q_ymin=, q_xmax=, q_ymax=)}")
# seed=None
# print(f"SRC_random [1,2,2,3]: {tree.SRC_random(q_xmin=1, q_ymin=2, q_xmax=2, q_ymax=3, seed=seed).bbox}")
# print(f"SRC_random [0,0,0,0]: {tree.SRC_random(q_xmin=0, q_ymin=0, q_xmax=0, q_ymax=0, seed=seed).bbox}")
# print(f"SRC_random [4,4,4,4]: {tree.SRC_random(q_xmin=4, q_ymin=4, q_xmax=4, q_ymax=4, seed=seed).bbox}")
# print(f"SRC_random [1,1,2,2]: {tree.SRC_random(q_xmin=1, q_ymin=1, q_xmax=2, q_ymax=2, seed=seed).bbox}")
# print("\n\n\n")

# # print(f"BRC []: {tree.linear_BRC(q_xmin=, q_ymin=, q_xmax=, q_ymax=)}")
# print(f"3DAG BRC [1,2,2,3]: {tree.linear_BRC(q_xmin=1, q_ymin=2, q_xmax=2, q_ymax=3)}")
# print(f"3DAG BRC [0,0,0,0]: {tree.linear_BRC(q_xmin=0, q_ymin=0, q_xmax=0, q_ymax=0)}")
# print(f"3DAG BRC [4,4,4,4]: {tree.linear_BRC(q_xmin=4, q_ymin=4, q_xmax=4, q_ymax=4)}")
# print(f"3DAG BRC [1,1,2,2]: {tree.linear_BRC(q_xmin=1, q_ymin=1, q_xmax=2, q_ymax=2)}")



