from genericpath import exists

from flask.cli import F

import New_3DAG
import KDTree_2D
import numpy as np 
import pandas as pd
import random
import os
import matplotlib.pyplot as plt


def make_queries(tree=None, num=1, seed=None, small=False, medium=False, large=False):
    if tree == None:
        print("We need a tree!")
        return
    if seed != None:
        random.seed(seed)

    #need to make 2 query lists, one for DAG and one for KD
    DAG_query_list = []
    KD_query_list = []
    if small == False and medium == False and large == False:
        return print("Need to set small, medium, or large to True")
    if small == True:
        coeff_num = int((tree.bbox[2]-tree.bbox[0])*0.1)
    if medium == True:
        coeff_num = int((tree.bbox[2]-tree.bbox[0])*0.2)
    if large == True:
        coeff_num = int((tree.bbox[2]-tree.bbox[0])*0.3)

    i=0
    while i < num:
        # #this is for semi random query box generation
        # xmin = random.randint(tree.bbox[0],tree.bbox[2]-coeff_num)
        # xmax = random.randint(xmin+1,xmin+coeff_num)
        # ymin = random.randint(tree.bbox[1],tree.bbox[3]-coeff_num)
        # ymax = random.randint(ymin+1,ymin+coeff_num)

        #this is for square query generation
        xmin = random.randint(tree.bbox[0],tree.bbox[2]-coeff_num)
        xmax = xmin + coeff_num
        ymin = random.randint(tree.bbox[0],tree.bbox[2]-coeff_num)
        ymax = ymin + coeff_num


        #Arranges the queries xmins and ymins
        if xmin > xmax:
            a = xmax
            xmax = xmin
            xmin = a
        if ymin > ymax:
            a = ymax
            ymax = ymin
            ymin = a

        #This limits the possible query ranges to the actual boundery box of the data set
        if xmin < tree.bbox[0]:
            xmin = tree.bbox[0]

        if xmax > tree.bbox[2]:
            xmax = tree.bbox[2]

        if ymin < tree.bbox[1]:
            ymin = tree.bbox[1]

        if ymax > tree.bbox[3]:
            ymax = tree.bbox[3]
        
        if ymax < tree.bbox[1]:
            ymax = tree.bbox[1]

        DAG_query_list.append([xmin, ymin, xmax, ymax])
        KD_query_list.append([(xmin,xmax),[ymin,ymax]])
        i+=1
    return DAG_query_list, KD_query_list



def stat_graph(path=None,title="",show=False):
    '''
    Need to input folder path, this will graph the SRC Depth files in the folder.
    This will look at the SRC_large.csv, then SRC_medium.csv, then SRC_small.csv.
    '''
    print("\tStarting Statistics Graphing...")
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
            
            i=0     #this is to find how many times a depth is returned by SRC from the SRC Query.csv file, note it may not return the maximum depth if the SRC Query.csv file
            value_list = []
            percent_list = []
            for item in range(src_data['Depth'].max()+1):
                value_list.append(src_data['Depth'].value_counts().get(i, 0))
                percent_list.append(f"{round(((value_list[i]/total_num)*100), 2)} %")
                i+=1
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
    print("\t\tCompleted Statistics Graphing")



def lvl_diff(DAGpath=None, KDpath=None, title=None, show=False, save=True):
    print("\tStarting Level Diff...")
    #makes sure that there is a slash at the end of the paths
    if DAGpath == None and KDpath == None:
        if path[len(path)-1] != '/':
            path = path + "/"
    
    #gets the csv files paths, these will be read then processed for graphing
    DAGitems = []
    for item in os.listdir(DAGpath):
        if item.__contains__('.csv'):
            DAGitems.append(item)

    KDitems = []
    for item in os.listdir(KDpath+'/SRC/'):
        if item.__contains__('.csv'):
            KDitems.append(item)

    #need to itterate through all csv files in folder
    for i in range(len(DAGitems)):
        DAG_list,KD_list=None,None
        DAG_list = pd.read_csv(DAGpath+DAGitems[i])['Depth']
        KD_list = pd.read_csv(KDpath+"SRC/"+KDitems[i])['Depth']
        #DAG_list and KD_list have the depths of returned nodes through SRC search
        #now finding the difference: DAG - KD          DAG will always be bigger, so if a negative value occurs something is terribly wrong

        if save == True:    #if true we save SRC Depths in csv file
            os.makedirs(DAGpath+"_Graphs/CSV/",exist_ok=True)
            os.makedirs(KDpath+"_Graphs/CSV/",exist_ok=True)
            temp_df = pd.DataFrame(columns=['DAG','KD'])
            temp_df['DAG'] = DAG_list
            temp_df['KD'] = KD_list
            temp_df.to_csv(DAGpath+f"_Graphs/CSV/{DAGitems[i].replace('.csv','_lvl_diff.csv')}")
            temp_df.to_csv(KDpath+f"_Graphs/CSV/{DAGitems[i].replace('.csv','_lvl_diff.csv')}")

        #finding diff
        diff_list = DAG_list - KD_list
        diff_list = diff_list.value_counts().sort_index()   #gets the # of times a # shows up in this series and sorts the final result
        diff_ind = diff_list.index.tolist()                 #gets index values from series

        #percentages
        percent_list = []
        # for j in range(len(diff_list)):
        for item in diff_list:
            try:
                # print(diff_list)
                # percent_list.append(f"{round((diff_list[j]/diff_list.sum())*100,2)}%")
                percent_list.append(f"{round((item/diff_list.sum())*100,2)}%")
            except KeyError:
                print("Error")
                percent_list.append("0.0%")
        
        #plotting
        bar = plt.bar(x=diff_ind,height=diff_list)
        # plt.figure(figsize=(8,8))
        plt.xticks(diff_ind)
        if title != None:
            plt.title(f"{title} ({DAGitems[i]})")
        else:
            plt.title(f"{DAGitems[i]}")
        plt.xlabel("Diff Size")

        #percentages
        j=0
        for p in bar:
            width = p.get_width()
            height = p.get_height()
            x, y = p.get_xy()

            plt.text(x+width/2, y+height*1.01,percent_list[j],ha='center',weight='bold')
            j+=1

        plt.tight_layout()
        os.makedirs(DAGpath+"_Graphs/Diff",exist_ok=True)
        # os.makedirs(KDpath+"_Graphs/Diff",exist_ok=True)
        plt.savefig(DAGpath+"_Graphs/Diff/"+str(DAGitems[i]).replace('.csv','.png'))
        # plt.savefig(KDpath+"_Graphs/Diff/"+str(DAGitems[i]).replace('.csv','.png'))
        if show == True:
            plt.show()
        else:
            plt.close('all')
    print("\t\tFinished Level Diff")



def L2norm(path=None, show=False):
    print("\tStarting L2 Norm...")
    os.makedirs(path+"_L2 Norm/",exist_ok=True)
    files = os.listdir(path)
    for csv_file in files:
        if csv_file.__contains__("SRC"):        #only gets csv files that are SRC Query, then gets the SRC Query.csv file's Depth, and then graphs it
            data = pd.read_csv((path+f"{csv_file}"))    #data will be equal to each original SRC file
            
            i=0     #this is to find how many times a depth is returned by SRC from the SRC Query.csv file, note it may not return the maximum depth if the SRC Query.csv file
            value_list = []
            for i in range(data['Depth'].max()+1):
                value_list.append(data['Depth'].value_counts().get(i, 0))
                # i+=1
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
                j=0
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
            else:
                plt.close('all')

    print("\t\tFinished L2 Norm\n")



def accuracy(path=None):
    #need to get SRC and BRC
    BRC_path = path+'BRC/'
    SRC_folders=[]
    for item in os.listdir(path):
        if item.__contains__('SRC'):
            SRC_folders.append(path+item+'/')

    BRC_files=[]
    for item in os.listdir(BRC_path):
        if item.__contains__('.csv'):
            BRC_files.append(BRC_path+item)     #will always be order of large, medium, small

    BRC_large = pd.read_csv(BRC_files[0])['Num Of Points']
    BRC_medium = pd.read_csv(BRC_files[1])['Num Of Points']
    BRC_small = pd.read_csv(BRC_files[2])['Num Of Points']

    
    for i in range(len(SRC_folders)):
        num_list=[]
        for item in os.listdir(SRC_folders[i]):
            if item.__contains__('.csv'):
                SRC_num = pd.read_csv(SRC_folders[i]+item)['Data Size']
                num_list.append(SRC_num.sum()/BRC_large.sum())
        with open(SRC_folders[i]+"Average.txt", 'w') as file:
            for item in num_list:
                file.write(str(item)+'\n')
        file.close()

                




def __main__(num=10, dataset=None, seed=None, rng=None, points=None):
    if points == None:
        points = []
        for i in range(rng):
            for j in range(rng):
                points.append((i,j))

    print(f"Starting {dataset} - {num}")


    DAGTREE = New_3DAG.DAGTree(points=points, axis=0, cutoff=4)
    KDTREE = KDTree_2D.KDTree(points=points, axis=0, cutoff=4)

    DAG_queries, KD_queries = make_queries(DAGTREE,num=num,seed=seed,small=True)

    things = os.listdir('3DAG and 2D Tree/')
    if things.__contains__('Saved Queries') == False:
        os.mkdir("Saved Queries")
    if os.listdir('3DAG and 2D Tree/Saved Queries/').__contains__(f"{dataset} - {num}") == False:
        os.mkdir(f"3DAG and 2D Tree/Saved Queries/{dataset} - {num}")
    path = f"3DAG and 2D Tree/Saved Queries/{dataset} - {num}"

    os.makedirs(path+"/DAG",exist_ok=True)
    os.makedirs(path+"/DAG/SRC Exhaustive",exist_ok=True)
    os.makedirs(path+"/DAG/SRC Middle",exist_ok=True)
    os.makedirs(path+"/DAG/SRC Random",exist_ok=True)
    os.makedirs(path+"/DAG/SRC Left and Right",exist_ok=True)
    os.makedirs(path+"/DAG/BRC",exist_ok=True)

    os.makedirs(path+"/KD",exist_ok=True)
    os.makedirs(path+"/KD/SRC",exist_ok=True)
    os.makedirs(path+"/KD/BRC",exist_ok=True)

    # ret = DAGTREE.get_all_nodes()
    # ret.to_csv(path+'/DAG/all_nodes.csv')

    print("\tStarting Small Queries...")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_exhaustive=True,path=path+"/DAG/SRC Exhaustive",small=True,save=True, name=f"DAG {dataset} SRC_exhaustive Small {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_middle=True,path=path+"/DAG/SRC Middle",small=True,save=True, name=f"DAG {dataset} SRC_middle Small {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_random=True,path=path+"/DAG/SRC Random",small=True,save=True, name=f"DAG {dataset} SRC_random Small {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_leftright=True,path=path+"/DAG/SRC Left and Right",small=True,save=True, name=f"DAG {dataset} SRC_leftright Small {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,BRC=True,path=path+"/DAG/BRC",small=True,save=True, name=f"DAG {dataset} BRC Small {num}")
    KDTree_2D.save_query(tree=KDTREE,query_list=KD_queries,SRC=True,path=path+"/KD/SRC",save=True,name=f"KD {dataset} SRC Small {num}")
    KDTree_2D.save_query(tree=KDTREE,query_list=KD_queries,BRC=True,path=path+"/KD/BRC",save=True,name=f"KD {dataset} BRC Small {num}")

    print("\tStarting Medium Queries...")
    DAG_queries, KD_queries = make_queries(DAGTREE,num=num,seed=seed,medium=True)
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_exhaustive=True,path=path+"/DAG/SRC Exhaustive",medium=True,save=True, name=f"DAG {dataset} SRC_exhaustive Medium {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_middle=True,path=path+"/DAG/SRC Middle",medium=True,save=True, name=f"DAG {dataset} SRC_middle Medium {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_random=True,path=path+"/DAG/SRC Random",medium=True,save=True, name=f"DAG {dataset} SRC_random Medium {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_middle=True,path=path+"/DAG/SRC Left and Right",medium=True,save=True, name=f"DAG {dataset} SRC_leftright Medium {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,BRC=True,path=path+"/DAG/BRC",medium=True,save=True, name=f"DAG {dataset} BRC Medium {num}")
    KDTree_2D.save_query(tree=KDTREE,query_list=KD_queries,SRC=True,path=path+"/KD/SRC",save=True,name=f"KD {dataset} SRC Medium {num}")
    KDTree_2D.save_query(tree=KDTREE,query_list=KD_queries,BRC=True,path=path+"/KD/BRC",save=True,name=f"KD {dataset} BRC Medium {num}")

    print("\tStarting Large Queries...\n")
    DAG_queries, KD_queries = make_queries(DAGTREE,num=num,seed=seed,large=True)
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_exhaustive=True,path=path+"/DAG/SRC Exhaustive",large=True,save=True, name=f"DAG {dataset} SRC_exhaustive Large {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_middle=True,path=path+"/DAG/SRC Middle",large=True,save=True, name=f"DAG {dataset} SRC_middle Large {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_random=True,path=path+"/DAG/SRC Random",large=True,save=True, name=f"DAG {dataset} SRC_random Large {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,SRC_middle=True,path=path+"/DAG/SRC Left and Right",large=True,save=True, name=f"DAG {dataset} SRC_leftright Large {num}")
    New_3DAG.save_query(tree=DAGTREE,query_list=DAG_queries,BRC=True,path=path+"/DAG/BRC",large=True,save=True, name=f"DAG {dataset} BRC Large {num}")
    KDTree_2D.save_query(tree=KDTREE,query_list=KD_queries,SRC=True,path=path+"/KD/SRC",save=True,name=f"KD {dataset} SRC Large {num}")
    KDTree_2D.save_query(tree=KDTREE,query_list=KD_queries,BRC=True,path=path+"/KD/BRC",save=True,name=f"KD {dataset} BRC Large {num}")

    stat_graph(path=path+"/DAG/SRC Exhaustive/",title=f"DAG Exh {dataset}")
    stat_graph(path=path+"/DAG/SRC Middle/",title=f"DAG Mid {dataset}")
    stat_graph(path=path+"/DAG/SRC Random/", title=f"DAG Rand {dataset}")
    stat_graph(path=path+"/DAG/SRC Left and Right/",title=f"DAG L&R {dataset}")
    stat_graph(path=path+"/DAG/BRC/", title=f"DAG BRC {dataset}")

    stat_graph(path=path+"/KD/SRC/", title=f"KD SRC {dataset}")
    stat_graph(path=path+"/KD/BRC/", title=f"KD BRC {dataset}")

    L2norm(path=path+"/DAG/SRC Exhaustive/")
    L2norm(path=path+"/DAG/SRC Middle/")
    L2norm(path=path+"/DAG/SRC Random/")
    L2norm(path=path+"/DAG/SRC Left and Right/")
    L2norm(path=path+"/KD/SRC/")
    

    lvl_diff(DAGpath=path+"/DAG/SRC Exhaustive/", KDpath=path+"/KD/")
    lvl_diff(DAGpath=path+"/DAG/SRC Middle/", KDpath=path+"/KD/")
    lvl_diff(DAGpath=path+"/DAG/SRC Random/", KDpath=path+"/KD/")
    lvl_diff(DAGpath=path+"/DAG/SRC Left and Right/", KDpath=path+"/KD/")

    accuracy(path=path+"/DAG/")
    accuracy(path=path+"/KD/")


    print(f"\nFinished {dataset} - {num}\n\n\n")












