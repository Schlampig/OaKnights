from es import *
TOP_K = 1  # set the number of answers you prefer Terra to return
ES_SEARCH = ES(top_k=TOP_K)  # initialize the database


print("- 泰拉苏醒 -")
print()

while True:
    q = input("向泰拉发问：")
    if q == "所有苦难都结束了":  # input this sentence could stop the running program
        break
    lst_res = ES_SEARCH.run(query=q)
    if len(lst_res) == 0:  # no answer found in database
        print("泰拉沉默")
    for res in lst_res:
        print("泰拉答：{}\n".format(res))
    print("-"*30)

print()
print("- 泰拉沉睡 -")
