import json

anime_lst={
    "no game no life":"game world",
    "random":"cum",
    "sex life":"none"
}

# load=json.dumps(anime_lst)
# print(load)


lst1=[1,2,3,4,5,6,7,8,9,10]

lst2=[12,34,76,84,97]

json_={
    "first_lst":[],
    "second_lst":lst2
}

for i in range(100):
    json_["first_lst"].append(i)
print(json_)

# load=json.dumps(json_,indent=4)
# # print(load)
# print(json.dumps(json_,indent=1))
