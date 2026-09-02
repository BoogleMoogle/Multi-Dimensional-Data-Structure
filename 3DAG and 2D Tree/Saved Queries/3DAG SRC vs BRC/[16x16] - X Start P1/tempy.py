import pandas as pd
import numpy as np
import os

def highlight_dup(data_frame):
    is_dup = data_frame.duplicated(subset=['Range [xmin, xmax] [ymin, ymax]'], keep=False)

    styles = np.full(data_frame.shape, '', dtype='<U50')

    styles[is_dup.values] = 'background-color: yellow'

    # is_dup = data_frame.duplicated(subset=['Mem Hex'], keep=False)

    # styles = np.full(data_frame.shape, '', dtype='<U50')

    # styles[is_dup.values] = 'background-color: red'

    return pd.DataFrame(styles, index=data_frame.index, columns=data_frame.columns)



os.chdir(r'C:\Users\cvinc\Desktop\College\Internship\Github\Multi-Dimensional-Data-Structure\3DAG and 2D Tree\Saved Query\3DAG SRC vs BRC\[16x16] - X Start P1')


df = pd.read_csv('tree.csv')

bbox_dup_count = df.duplicated(subset=['Range [xmin, xmax] [ymin, ymax]']).sum()
hex_dup_count = df.duplicated(subset=['Mem Hex']).sum()

# style_df = df['Range [xmin, xmax] [ymin, ymax]',['Mem Hex']]

df = df.style.apply(highlight_dup, axis=None)
df.to_excel('tree_edited.xlsx')


# print(df[df.duplicated(keep=False)])
print(f"BBOX Dups: {bbox_dup_count}\nMem Hex Dups: {hex_dup_count}")


