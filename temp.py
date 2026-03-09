import plotly.express as px
import pandas as pd
import numpy as np

### Graphing with matplot takes way too long, so I want to try using plotly and dash ###

path = r"C:\Users\cvinc\Desktop\College\Internship\WarmUp\Saved KD Trees\Tests\house_data.csv"
csv_data = pd.read_csv(path)
csv_data = csv_data.values.tolist()
# this gives us id, data, price, bedrooms, bathrooms, sqft_living, sqft_lot, floors, waterfront, view, condition, grade, sqft_above, sqft_base, yr_built, yr_renovated, zipcode, lat, long, sqft_living15, sqft_lot15
# we want item[17] and item[18]
points = []
for item in csv_data:
    points.append((item[17],item[18]))

x=[]
y=[]
for item in points:
    x.append(item[0])
    y.append(item[1])

fig = px.scatter(x=x, y=y)

# fig.add_vline(x=47.4, line_width=1, line_dash="dash", line_color="red")
fig.add_shape(type="line", x0=47.4, x1=47.4, y0=-122.4, y1=-122.2, line=dict(color="Red",width=2,dash="dash"))
fig.show()










