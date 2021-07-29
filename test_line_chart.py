# import numpy as np
# import pandas as pd

# import mysql.connector
# from dotenv import load_dotenv
# load_dotenv()

# db=mysql.connector.connect(
#     host="localhost",
#     user="root",
#     passwd="Dartagnan19@",
#     database="testdatabase"
#     )

# mycursor=db.cursor(buffered=True)


# users=[]
# lst=[]
# mycursor.execute("SELECT * FROM Twitter_Users")
# user=mycursor.fetchall()
# for i in user:
#     users.append(i)

# row_headers=[x[0] for x in mycursor.description] #this will extract row headers

# data=[]
# admin_user=dict(zip(row_headers,users))
# # print(admin_user)

# for i in users:
#     data.append(dict(zip(row_headers,i)))
# # print(data)

# df=pd.DataFrame(data)
# print(df)



# df.to_excel("Twitter Users.xlsx") 


import matplotlib.pyplot as plt

months = ["Jan","Feb","Mar","Apr","Jun","Jul","Aug"]
num_of_post = [9.8,12,8,7.2,6.9,7,7.8]

plt.plot(months, num_of_post)
plt.title('Unemployment Rate Vs Year')
plt.xlabel('Months')
plt.ylabel('Post each Month')
plt.savefig('./static/preview_img/twitter analytics.png')
plt.show()
