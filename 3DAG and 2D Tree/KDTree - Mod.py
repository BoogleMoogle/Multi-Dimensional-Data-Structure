import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np
import os
#to see stack
import inspect
np.set_printoptions(legacy='1.25')








class KDTree:
    def __init__(self,points=[],depth=0,axis=0,split_value=[],bbox=[],left=None,right=None,parent=None,cutoff=1):
        
        self.data_size = len(points)
        self.split_value = split_value
        self.depth = depth
        self.axis = axis
        self.bbox = bbox
        # self.children = children
        self.parent = parent
        self.left = left
        self.right = right
        self.cutoff = cutoff

        self.dimensionality = len(points[0])
        points.sort(key=lambda x: x[self.axis])
        self.points = points

        if self.bbox == []:
            self.bbox = self.find_bbox()
        #bbox is a tuple, each tuplr is the [min, max] of each dimension

        if self.data_size > cutoff:
            self.split()


    def __str__(self):
        if self.split_value != []:
            return f"Split Node: {self.axis} = {self.split_value}, Level: {self.depth}, BBOX: {self.bbox}"#, Left: {self.left}, Right: {self.right}"

        else:
            return f"{self.points}"


    def find_bbox(self):
        bbox = []
        points = pd.DataFrame(self.points)
        for i in range(len(points.columns)):
            bbox.append((points[i].min(),points[i].max()))
        return bbox


    def split(self):
        #it is important to mention that this is KD Tree, we still only have left and right children
        #need to find middle of data, for each dimension

        self.split_value = self.points[len(self.points)//2][self.axis]
        
        left = []
        right = []
        #dependent on the axis original node is on
        for j in range(len(self.points)):
            if self.split_value <= self.points[j][self.axis]:
                right.append(self.points[j])
            else:
                left.append(self.points[j])

        if left == [] or right == []:
            return
        if self.parent != None and self.parent.data_size == self.data_size:
            return
        #need to find bbox seperately
        #the axis that we are splitting on is the most improtant, it is what becomes left's max and right's min
        # print(self.split_value)     #<- this value is what actually changes, everything else stays the same
        #the only thing we need to worry about is the changing axis
        left_bbox = []
        right_bbox = []
        for i in range(self.dimensionality):
            left_bbox.append(0)
            right_bbox.append(0)
        left_bbox[self.axis] = [self.bbox[self.axis][0],self.split_value]
        right_bbox[self.axis] = [self.split_value,self.bbox[self.axis][1]]
        for i in range(self.dimensionality-1):
            left_bbox[(self.axis+(i+1))%self.dimensionality] = self.bbox[(self.axis+(i+1))%self.dimensionality]
            right_bbox[(self.axis+(i+1))%self.dimensionality] = self.bbox[(self.axis+(i+1))%self.dimensionality]

        self.left = KDTree(points=left,depth=self.depth+1,axis=(self.axis+1)%self.dimensionality,parent=self,cutoff=self.cutoff,bbox=left_bbox)
        self.right = KDTree(points=right,depth=self.depth+1,axis=(self.axis+1)%self.dimensionality,parent=self,cutoff=self.cutoff,bbox=right_bbox)
        self.points = None       #<- want points in each node? (Note, uses more meory)


    def SRC(self,query=[], best=None):
        in_range = 0
        for i in range(len(self.bbox)):
            if self.bbox[i][0] <= query[i][0] and self.bbox[i][1] >= query[i][1]: #this node 100% contains the range
                in_range +=  1
    
        #we only want nodes in the range, this checks that
        if in_range == self.dimensionality:
            if best == None or best.depth < self.depth:
                best = self

            #left
            if self.left != None:
                in_range = 0
                for j in range(len(self.left.bbox)):    #checking left bbox, to see if it's in range
                    if self.left.bbox[j][1] >= query[j][1]:
                        in_range += 1
                if in_range == self.left.dimensionality:    #will only go left if the left node is in range for all dimensions
                    return self.left.SRC(query, best)

            #right 
            if self.right != None:
                in_range = 0
                for j in range(len(self.right.bbox)):   #checking right bbox, to see if it's in range
                    if self.right.bbox[j][0] <= query[j][0]:
                        in_range +=1
                if in_range == self.right.dimensionality:   #will only go right if the right node is in range for all dimensions
                    return self.right.SRC(query, best)

        return best


    def linear_BRC(self, query):
        nodes = None
        nodes = self.get_leaf_linear(boxes=[])

        temp = []
        for item in nodes:
            for thing in item:
                temp.append(thing)
        
        returning_list = []
        for item in temp:
            in_range = 0
            for i in range(len(query)):
                if query[i][0] <= item[i] and query[i][1] >= item[i]:   #if node is in range (dependent on axis) increase in_range by 1
                    in_range += 1

            if in_range == self.dimensionality:     #this means for all 3 dimensions this node is in range of query
                returning_list.append(item)
        
        return returning_list

    
    def get_leaf_linear(self, boxes=[]):
        if self.points != None:
            boxes.append(self.points)
        if self.left != None:
            self.left.get_leaf_linear(boxes)
        if self.right != None:
            self.right.get_leaf_linear(boxes)
        return boxes


    def print_tree(self, points=False, file=False, title=None):
        if type(title) != str:
                    title = "Printed_KDTree.txt"
        else:
            if title.__contains__('.txt') == False:
                title = f"{title}.txt"
        if points == True:
            if self.points != None and self.left == None and self.right == None:
                if file == False:
                    print(self.points)
                else:
                    with open(f'{title}', 'a') as file:
                        file.write(f"{self.points}\n")
                        file.close()
        elif points == None:
            if self.points == None and self.left != None and self.right != None:
                if file == False:
                    print(self)
                else:
                    with open(f'{title}', 'a') as file:
                        file.write(f"{self.__str__()}\n")
                        file.close()
        else:
            if file == False:
                print(self)
            else:
                with open(f'{title}', 'a') as file:
                        file.write(f"{self.__str__()}\n")
                        file.close()

        if self.left != None:
            self.left.print_tree(points,file=file,title=title)
        if self.right != None:
            self.right.print_tree(points,file=file,title=title)







####################### GENERAL METHODS #######################
def points_from_file(path=None,columns=None,file_extension=None,drop_duplicates=False,gowala=False,limit=1000):        #Need to make it where it can split the csv file with delimeter = ' ' or ','. Also make method to work with .txt
    if path == None:
        return print("Need path!")
    
    if gowala==True:
        if limit == False or limit == None:
            points = pd.read_csv(path,sep='\t',header=None,usecols=columns,names=['Lat','Long'])
        else:
            points = pd.read_csv(path,sep='\t',header=None,usecols=columns,names=['Lat','Long'],nrows=limit)
        points = points.dropna()
        # points['timestamp'] = pd.to_datetime(points['timestamp'],format="%Y-%m-%dT%H:%M:%SZ")
        #make time stamp into seconds
        # points['timestamp'] = (points['timestamp'] - pd.Timestamp("2009-02-01")).dt.total_seconds().astype(int)
    elif file_extension == 'csv':
        points = pd.read_csv(path)
        # points = points.dropna(how='any')
    elif file_extension == 'excel':
        points = pd.read_excel(path)
    else:
        points = pd.read_csv(path)
        # points = points.dropna(how='any')

    if columns != None:
        if gowala != True:
            points = points[columns]
            if file_extension=='csv':
                points = points.dropna()

    if drop_duplicates == True:
        points = points.drop_duplicates()

    points = points.values.tolist()
    return points

#only works in 2D right now
def make_points(num=1, sprout=None, aRang=0, bRang=100):
    temp = []
    if sprout != None:
        random.seed(sprout)
    while len(temp) < num:
        temp.append((random.randint(aRang,bRang),random.randint(aRang,bRang)))
    return temp


def save_query(tree,num=1,path=None,SRC=True,BRC=False,save=True,show=False,query_list=[]):
    if path == None:
        things = os.listdir('.')
        if things.__contains__('Saved Query') == False and things.__contains__('Saved Queries') == False:
            os.mkdir("Saved Query")
        path = f"Saved Query/temp {len(os.listdir('Saved Query'))+1}.csv"
    
    for i in range(len(query_list)):
        if SRC == True:
            node = tree.SRC(query=query_list[i])
        elif BRC == True:
            node = tree.linear_BRC(query=query_list[i])

        # print(query_list[i])

        if SRC == True:
            if i == 0:
                temp = pd.DataFrame(columns=["SRC Query","Depth","BBoxes","Data Size"], index=None)
 
            temp.loc[i] = [[query_list[i]],node.depth,node.bbox,node.data_size]

        elif BRC == True:
            if i == 0:
                temp = pd.DataFrame(columns=["BRC Query","Data Size"], index=None)       #removed "Points"
            temp.loc[i] = [[query_list[i]],len(node)]
    
    if save == True:
        try: 
            df = pd.read_csv(path)
            temp.to_csv(path,mode='w',index=None)
        except Exception:
            temp.to_csv(path,mode='a',columns=None,index=None)
    else:
        return print(temp)


def SRC_vs_BRC(tree, num=1, sprout=None, path=None, show=False, duplicates=False, starting_per=0.30, interval=10, SRC=True, BRC=True, force_old=False, pre_list=None):
    if tree == None:
        return print("Need tree!!!")
    if path == None:
        return print("Need path to query folder!")
    if sprout == None:
        return print("Need a sprout!")
    
    random.seed(sprout)

    if duplicates == None:
        return print("Need to state whether or not this tree was made with duplicate points!")
    if path[len(path)-1] != "/":
        path = path+"/"
    
    print("Starting Queries...")

    coeffs_list = []
    #Setting Coeffs
    for j in range(int(round((starting_per*100) / interval,0))+1):
        coeffs_list.append(((starting_per*100) - (interval*j))/100)
    #we have coefficents list, now we need to make a csv file for every item in it

    for i in range(len(coeffs_list)):
        if coeffs_list[i] <= 0:
            coeffs_list.remove(coeffs_list[i])  #we hit either 0 or a negative num for coeffs
            break
        if pre_list == None:
            # coeff_num = (tree.bbox[0][1] - tree.bbox[0][0]) *coeffs_list[i]
            query_list = []
            for j in range(num):
                temp_list = []
                if force_old == False:
                    for k in range(len(tree.bbox)):
                        coeff_num = (tree.bbox[k][1] - tree.bbox[k][0]) *coeffs_list[i]
                        #making queries min and max
                        temp_min = random.uniform(tree.bbox[k][0],tree.bbox[k][1]-coeff_num)
                        temp_max = random.uniform(temp_min+1,temp_min+coeff_num)
                        #limits mins and max to only be inside the tree
                        if temp_min < tree.bbox[k][0]:
                            temp_min = tree.bbox[k][0]
                        if temp_max > tree.bbox[k][1]:
                            temp_max = tree.bbox[k][1]

                        temp_list.append((temp_min,temp_max))
                else:
                    coeff_num = (tree.bbox[0][1]-tree.bbox[0][0])*coeffs_list[i]
                    # xmin = random.uniform(tree.bbox[0][0],tree.bbox[0][1]-coeff_num)
                    # xmax = random.uniform(xmin+1,xmin+coeff_num)
                    # ymin = random.uniform(tree.bbox[1][0],tree.bbox[1][1]-coeff_num)
                    # ymax = random.uniform(ymin+1,ymin+coeff_num)

                    #some old data is roudned by 2, for some reason??
                    xmin = random.uniform(tree.bbox[0][0],tree.bbox[0][1]-coeff_num)
                    xmax = random.uniform(xmin+1,xmin+coeff_num)
                    ymin = random.uniform(tree.bbox[1][0],tree.bbox[1][1]-coeff_num)
                    ymax = random.uniform(ymin+1,ymin+coeff_num)

                    if xmin < tree.bbox[0][0]:
                        xmin = tree.bbox[0][0]
                    if xmax > tree.bbox[0][1]:
                        xmax = tree.bbox[0][1]
                    if ymin < tree.bbox[1][0]:
                        ymin = tree.bbox[1][0]
                    if ymax > tree.bbox[1][1]:
                        ymax = tree.bbox[1][1]  
                    if ymax < tree.bbox[1][0]:
                        ymax = tree.bbox[1][0]

                    temp_list=[(xmin,xmax),(ymin,ymax)]
                
                query_list.append(temp_list)

            if SRC == True:
                SRC_path = f"{path}SRC_KD_{coeffs_list[i]:.2f}.csv"
                print(f"\tStarting SRC at {coeffs_list[i]:.2f}...")
                save_query(tree=tree,num=1,path=SRC_path,SRC=True,BRC=False,save=True,show=show,query_list=query_list)
                print(f"\tFinished SRC at {coeffs_list[i]:.2f}")

            if BRC == True:
                BRC_path = f"{path}BRC_KD_{coeffs_list[i]:.2f}.csv"
                print(f"\n\tStarting BRC at {coeffs_list[i]:.2f}...")
                save_query(tree=tree,num=1,path=BRC_path,SRC=False,BRC=True,save=True,show=show,query_list=query_list)
                print(f"\tFinished BRC at {coeffs_list[i]:.2f}\n")
    
    if pre_list != None:
        b=0
        for i in range(len(pre_list)):
            if coeffs_list[(len(coeffs_list)-1)-i] < 0:
                pass
            query_list = pre_list[b]
            if SRC == True:
                SRC_path = f"{path}SRC_{coeffs_list[(len(coeffs_list)-1)-i]:.2f}.csv"
                print(f"\tStarting SRC at {coeffs_list[(len(coeffs_list)-1)-i]:.2f}...")
                save_query(tree=tree,num=1,path=SRC_path,SRC=True,BRC=False,save=True,show=show,query_list=query_list)
                print(f"\tFinished SRC at {coeffs_list[(len(coeffs_list)-1)-i]:.2f}")

            if BRC == True:
                BRC_path = f"{path}BRC_{coeffs_list[(len(coeffs_list)-1)-i]:.2f}.csv"
                print(f"\n\tStarting BRC at {coeffs_list[(len(coeffs_list)-1)-i]:.2f}...")
                save_query(tree=tree,num=1,path=BRC_path,SRC=False,BRC=True,save=True,show=show,query_list=query_list)
                print(f"\tFinished BRC at {coeffs_list[(len(coeffs_list)-1)-i]:.2f}\n")
            b+=1
    print("\nFinished SRC and BRC Queries\n")


def statistics(file_path=None,graph=False,show=False):
    '''
    F/P% is found by (SRC Size/BRC Size)
    Error % is found by (BRC Size / SRC Size)*100

    When calculating the average F/P % we remove values that are inf, the # of inf values we removed is recorded in the summary.txt file in report as "Tot # of Inf".
    The F/P % is suppose to represent how incorrect our SRC search size is, compared to our BRC search size.
    '''
    if file_path == None:
        return print("We need a path!")
    print("Starting Statistics...")
    
    if file_path[len(file_path)-1] != "/":
        file_path = file_path+"/"

    os.makedirs(file_path+"_Report/", exist_ok=True)

    for item  in os.listdir(file_path):
        df = pd.DataFrame(columns=['BRC Size','SRC Size','SRC Depth','Diff','F/P %','Error %'])
        if item.__contains__('.csv') and item.__contains__('BRC'):
            df['BRC Size'] = pd.read_csv(file_path + item)['Data Size']
            df['SRC Size'] = pd.read_csv(file_path + item.replace('BRC','SRC'))['Data Size']
            df['SRC Depth'] = pd.read_csv(file_path + item.replace('BRC','SRC'))['Depth']
            df['Error %'] = ((df['BRC Size']/df['SRC Size']))*100
            df['F/P %'] = (df['SRC Size']/df['BRC Size'])
            df['Diff'] = df['SRC Size'] - df['BRC Size']
            #change inf values to 100% for Error %
            df['Error %'] = df['Error %'].replace([np.inf,-np.inf],100)
            #get num of inf in F/P %
            df_total_inf = np.isinf(df['F/P %']).values.sum()
            df.to_csv(file_path+f"_Report/{item.replace('BRC_','')}")

            #this is for summary
            df_avg_BRC_size = round(df['BRC Size'].mean(),2)
            df_avg_SRC_size = round(df['SRC Size'].mean(),2)
            df_avg_SRC_depth = round(df['SRC Depth'].mean(),2)
            df_avg_diff = round(df['Diff'].mean(),2)
            df_avg_fp = round(df.replace([np.inf, -np.inf],np.nan).dropna()['F/P %'].mean(),2)
            df_avg_error = round(df['Error %'].mean(),2)

            with open(file_path+"_Report/_Summary.txt", 'a') as file:
                file.write(f"{item.replace('BRC_','').replace('.csv','')}\n\tBRC Size:\t{df_avg_BRC_size:,}\n\tSRC Size:\t{df_avg_SRC_size:,}\n\tSRC Depth:\t{df_avg_SRC_depth:,}\n\tDiff:\t\t{df_avg_diff:,}\n\tF/P %:\t\t{df_avg_fp:,}%\n\tError %:\t\t{df_avg_error:,}%\n\tTot # of Inf: {df_total_inf:,}\n\n\n")
            if graph == True:
                stat_graph(file_path,show=show)
    print("Finished Statistics\n")


def stat_graph(path=None,title="",show=False):
    '''
    Need to input folder path, this will graph the SRC Depth files in the folder.
    This will look at the SRC_large.csv, then SRC_medium.csv, then SRC_small.csv.
    '''
    print("Starting Statistics Graphing...")
    if path == None:
        return print("Need path!")
    if path[len(path)-1] != "/":
        path = path+"/"
    os.makedirs(f"{path}_Graphs", exist_ok=True)     #makes Graphs folder if one isn't already made
    
    if title != "":
        title = f": {title}"

    files = os.listdir(path)
    for csv_file in files:
        if csv_file.__contains__("SRC"):        #only gets csv files that are SRC Query, then gets the SRC Query.csv file's Depth, and then graphs it
            src_data = pd.read_csv((path+f"{csv_file}"))
            # src_depth = src_data['Depth']
            total_num = len(src_data['Depth'])  #normally should be 100,0000
            
            #this is to find how many times a depth is returned by SRC from the SRC Query.csv file, note it may not return the maximum depth if the SRC Query.csv file
            value_list = []
            percent_list = []
            for i in range(src_data['Depth'].max()+1):
                value_list.append(src_data['Depth'].value_counts().get(i, 0))
                percent_list.append(f"{round(((value_list[i]/total_num)*100), 2)} %")

            #this gets the depth of nodes returned 
            x_cord = []
            for j in range(len(value_list)):
                x_cord.append(j)

        
            ###maybe include something that gets the leaf nodes then checks all leaf nodes depth, gets max depth, and list it in the legend of the bar graph

            #making graph
            plt.figure(figsize=(8,8))
            bar = plt.bar(x_cord,value_list,width=0.6)
            plt.title(f"{str(csv_file).replace('.csv','')}{title}")
            # ax.bar(x_cord,value_list,width=0.6)

            #putting percentages on bars
            i=0
            for p in bar:
                width = p.get_width()
                height = p.get_height()
                x, y = p.get_xy()

                plt.text(x+width/2, y+height*1.01,percent_list[i],ha='center',weight='bold')
                i+=1
            
            plt.tight_layout()
            plt.savefig(f'{path}/_Graphs/{str(csv_file).replace('.csv','.png')}')
            if show == False:
                plt.close()
            else:
                plt.show()
    print("Completed Statistics Graphing\n")


def L2norm(path=None, show=False):
    if path == None:
        return print("Need query folder path!")
    #need to get data of SRC Depths and subtract it from the/a total distribution.
    print("Starting L2 Norm...")

    if path[len(path)-1] != "/":    #makes path accessable
                path = path+"/"
    os.makedirs(f"{path}_L2 Norm", exist_ok=True)    #makes L2 Norm folder
    files = os.listdir(path)
    for csv_file in files:
        if csv_file.__contains__("SRC"):        #only gets csv files that are SRC Query, then gets the SRC Query.csv file's Depth, and then graphs it
            data = pd.read_csv((path+f"{csv_file}"))    #data will be equal to each original SRC file

            #this is to find how many times a depth is returned by SRC from the SRC Query.csv file, note it may not return the maximum depth if the SRC Query.csv file
            value_list = []
            for i in range(data['Depth'].max()+1):
                value_list.append(data['Depth'].value_counts().get(i, 0))

            for j in range(len(value_list)):
                value_list[j] = value_list[j]/len(data['Depth'])
            #value list has the original data from SRC file
            columns_li = []
            for i in range(len(value_list)):
                columns_li.append(i)
            stored_data = pd.DataFrame(columns=['L2 Norm'])

            randomized_sample = data['Depth'].sample(n=len(data))   #randomized_sample fully randomly samples the entire data set
            #need to make columns of the first 100 points, then again for the first and next 100 (200 total), then containue
    
            #this is going through the randomly sampled data (SRC Depth) and going through it for every 100 points
            for i in range(int(randomized_sample.shape[0]/100)):
                temp = randomized_sample.head(100*(i+1))
                temp_value_list = []

                for j in range(randomized_sample.max()+1):   #this gets the depths of the nodes
                    temp_value_list.append(temp.value_counts().get(j, 0))

                #temp_value_list has the # of returned nodes of this random sample, want %
                for j in range(len(temp_value_list)):
                    temp_value_list[j] = temp_value_list[j]/(100*(i+1))
                temp_row = []
                temp_val = 0
                for k in range(len(temp_value_list)):
                    # for j in range(len(temp_value_list[k])):
                    temp_val += ((temp_value_list[k]-value_list[k])**2)
                    # temp_row.append(((temp_value_list[k]-value_list[k])**2)**0.5)       #this is the L2 norm as: ((sample - original)^2)^1/2
                temp_row.append((temp_val)**0.5)
                stored_data.loc[len(stored_data)] = temp_row
            stored_data.to_csv(f"{path}/_L2 Norm/{csv_file}")

            #need to save figure (scatter)
            stored_data = stored_data.values.tolist()

            x=[]
            for i in range(len(stored_data)):
                x.append(i)
            plt.figure(figsize=(16,10))
            plt.scatter(x,stored_data,marker='*', color='grey')
            plt.xlabel("Distribution")
            plt.ylabel("L2 Norm Val")
            plt.ylim(bottom=0)
            plt.xlim(left=0)
            plt.title(f"{csv_file.replace('.csv','')}")
            plt.tight_layout()
            os.makedirs(path+"_L2 Norm/Pictures",exist_ok=True)
            plt.savefig(path+f"_L2 Norm/Pictures/{csv_file.replace('.csv','.png')}")
            if show == True:
                plt.show()
    print("Finished L2 Norm\n")


def get_queries_from_old_data(path):
    '''
    I had to made a method that would get queries from a 3DAG file because I changed the format of bbox for this modular KD Tree. All you need to input is the path to 3DAG, then take what is returned then put it into the SRC_vs_BRC method.
    '''
    return_list = []
    for item in os.listdir(path):
        if item.__contains__('.csv') and item.__contains__('SRC'):
            query_list = None
            query_list = pd.DataFrame(pd.read_csv(path+item)['SRC Query'])
            query_list = query_list.values.tolist()
            temp_list = []
            for thing in query_list:
                temp_list.append(((thing[0]).replace('[','').replace(']','')).split(","))
            temp_list2 = []
            for i in range(len(temp_list)):
                temp_list2.append([(float(temp_list[i][0]),float(temp_list[i][2])),(float(temp_list[i][1]),float(temp_list[i][3]))])
            return_list.append(temp_list2)
    return return_list



##############################################################

### Gowala ###      social netowrk
path = r"Saved Datasets/Gowalla_totalCheckins.txt"
points = points_from_file(path,columns=[2,3],file_extension='csv',drop_duplicates=True,gowala=True,limit=300000)
#___________________________________________________________________________#


print(f"# of points: {len(points)}")
print("Making Tree...")
temp = KDTree(points,cutoff=4)
print("Tree Made\n")

### CONTROL PANNEL ###
num = 10000
sprout = 1
dataset ="Gowalla - 120,143 points"
# dataset =f"Uniform - [100 x 100]"
dup = False
itterations = 1
interval = 4
starting_per = 0.30
SRC = True
BRC = True
force_old = True
######################


if dup == False:
    dup = "Without Duplicates"
else:
    dup = "With Duplicates"



for i in range(itterations):
    pre_list=None

    ### This bit is only if you are reading data from 3DAG Tree, comment out if you aren't using this ###
    path = r"Saved Query/3DAG SRC vs BRC/{}/{}/{} - {}/".format(dataset, dup, sprout+i, f"{num:,}")
    pre_list = get_queries_from_old_data(path)
    ################################################################

    os.makedirs(r"Saved Query/KD SRC vs BRC/{}/{}".format(dataset,dup), exist_ok=True)
    path = r"Saved Query/KD SRC vs BRC/{}/{}/{} - {}/".format(dataset,dup,(sprout+i),f"{num:,}")
    os.makedirs(path,exist_ok=True)
    SRC_vs_BRC(tree=temp,num=num,sprout=sprout+i,path=path,show=False,duplicates=False,starting_per=starting_per,interval=interval,SRC=SRC,BRC=BRC,force_old=True,pre_list=pre_list)

    statistics(path,graph=True)
    L2norm(path)
print("KDTree done!!\n"+"_"*50)

##############################################################################



##### DATASETS #####
    #All /SHOULD/ automatically be set to drop duplicates

# ### CRAWDAD spitz/cellular Dataset Dropping Duplicates ###
# path = r"Saved Datasets/DT-mobile-data.csv/VDS_MS_310809_27_0210.csv"
# points = points_from_file(path,columns=['Laenge','Breite'],file_extension='csv',drop_duplicates=True)
# #___________________________________________________________________________#


# ### SRFG-v1 ###
# path = r"Saved Datasets/Check/SRFG-v1.csv"
# points = points_from_file(path,columns=['lat','long'],file_extension='csv',drop_duplicates=True)
# #___________________________________________________________________________#

# ### Inventory of Owned & Leased Properties (IOLP) ###
# building_path = r"Saved Datasets/Inventory of Owned and Leased Properties/2026-2-20-iolp-buildings.xlsx"
# lease_path = r"Saved Datasets/Inventory of Owned and Leased Properties/2026-2-20-iolp-leases.xlsx"

# points = points_from_file(lease_path,columns=['Latitude','Longitude'],file_extension='excel',drop_duplicates=True)
# building_points = points_from_file(building_path,columns=['Latitude','Longitude'],file_extension='excel',drop_duplicates=True)
# #_____________________________________________________________________________#


# ### Spatial Database NO Duplication ###
# path = r"Saved Datasets/Spatial.xlsx"
# points = points_from_file(path,columns=['lon','lat'],file_extension='excel',drop_duplicates=True)
# #___________________________________________________________________________#


# ### House ###
# path = r"Saved Datasets/house_data.csv"
# points = points_from_file(path,columns=['price','bedrooms','sqft_living'],file_extension='csv',drop_duplicates=True)
# #___________________________________________________________________________#


# ### Gowala ###      social netowrk
# path = r"Saved Datasets/Gowalla_totalCheckins.txt"
# points = points_from_file(path,columns=[1,2,3],file_extension='csv',drop_duplicates=True,gowala=True,limit=1000)
# #___________________________________________________________________________#


### Template for SRC path and BRC path ###
# SRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/"
# BRC_path = r"Saved Query/3DAG SRC vs BRC/Spatial/"
















