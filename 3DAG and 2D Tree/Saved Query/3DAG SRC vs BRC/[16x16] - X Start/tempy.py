import pandas as pd
import os


os.chdir(r'C:\Users\cvinc\Desktop\College\Internship\Github\Multi-Dimensional-Data-Structure\3DAG and 2D Tree\Saved Query\3DAG SRC vs BRC\[16x16] - X Start')


df = pd.read_csv('tree.csv')

dup_count = df.duplicated(subset=['Range [xmin, xmax] [ymin, ymax]']).sum()

print(df[df.duplicated(keep=False)])
print(dup_count)


