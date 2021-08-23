from oak_predict import predict


print("- 你好，博士 -")
print()

while True:
    q = input("问：")
    if q == "我问完了":
        break
    ans = predict(q)
    print("“{}”\n".format(ans))
    print("-"*30)

print()
print("- 再见，博士 -")