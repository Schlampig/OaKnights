import pandas as pd
from tqdm import tqdm


def add_operator_relation(load_entity, load_relation, load_cp, save_relation):
    """
    在原有图谱中添加自定义干员关系（operator_cp.xlsx须严格按格式填写）
    :param load_entity: string, path of operator_entity.csv
    :param load_relation: string, path of operator_relation.csv
    :param load_cp: string, path of operator_cp.xlsx
    :param save_relation: string, path of operator_relation_new.csv
    :return: None
    """
    print("- 开始添加 -")
    # 获取干员实体对应的id
    d_operator = dict()  # d_operator = {干员中文代号: 干员id}
    df_entity = pd.read_csv(load_entity)
    for i_entity in range(df_entity.shape[0]):
        if df_entity.loc[i_entity, ":LABEL"] == "中文代号":
            code_now = df_entity.loc[i_entity, "name"]
            id_now = df_entity.loc[i_entity, ":ID(node)"]
            if code_now not in d_operator.keys():
                d_operator[code_now] = str(id_now)
    # 在关系表后面拼接新关系
    lst_type = list()  # 记录人际关系类型
    df_relation = pd.read_csv(load_relation)
    df_cp = pd.read_excel(load_cp)
    for i_cp in tqdm(range(df_cp.shape[0])):
        head_id = d_operator.get(df_cp.loc[i_cp, "干员代号（A）"], None)
        tail_id = d_operator.get(df_cp.loc[i_cp, "干员代号（B）"], None)
        relation_h2t = df_cp.loc[i_cp, "B的R是A（A-R->B）"]
        relation_t2h = df_cp.loc[i_cp, "A的R是B（B-R->A）"]
        if head_id is not None and tail_id is not None:
            if relation_h2t != "无":
                r_now = pd.DataFrame({":START_ID(node)": [head_id], ":END_ID(node)": [tail_id],
                                      ":TYPE": [relation_h2t], "name": [relation_h2t]})
                df_relation = df_relation.append(r_now)
                lst_type.append(relation_h2t)
            if relation_t2h != "无":
                r_now = pd.DataFrame({":START_ID(node)": [tail_id], ":END_ID(node)": [head_id],
                                      ":TYPE": [relation_t2h], "name": [relation_t2h]})
                df_relation = df_relation.append(r_now)
                lst_type.append(relation_t2h)
    # 存储新关系
    df_relation.to_csv(save_relation, index=False, encoding="utf-8-sig")

    # 打印示例查询语句
    lst_type = list(set(lst_type))  # type类型去重
    print_type = "|".join(["`" + t + "`" for t in lst_type])
    print()

    print("说明：匹配的基本语法结构为：MATCH path=()-[]->() WHERE y RETURN x LIMIT z")
    print("其中，()内写点的类型，[]内写边的类型，y控制类型的属性，x表示想要返回的结果，z表示对结果数量的限制。")
    print()

    print("示例1：显示指定干员A的所有信息")
    print("格式：MATCH path=(n:中文代号)<--() WHERE n.name=\"A\" RETURN path")
    print("A=刻刀：MATCH path=(n:中文代号)<--() WHERE n.name=\"刻刀\" RETURN path")
    print()

    print("示例2：显示满足R属性的N名干员信息, 若需显示该属性下所有干员信息，则去掉LIMIT N")
    print("格式：MATCH path=()-[r:`R`]->() RETURN path LIMIT N")
    print("R=星座，N=15：MATCH path=()-[r:`星座`]->() RETURN path LIMIT 15")
    print()

    print("示例3：显示类型R中属性为X的所有干员")
    print("格式：MATCH path=(n:R {name:\"X\"})-[]->() RETURN path")
    print("R=种族，X=萨卡兹：MATCH path=(n:种族 {name:\"萨卡兹\"})-[]->() RETURN path")
    print()

    print("示例4：查找干员A与干员B之间的最短路径：")
    print("格式：MATCH path=shortestpath((n:中文代号)-[r:`活跃领域`|" + print_type + "*]->(m:中文代号)) WHERE n.name=\"A\" AND m.name=\"B\" RETURN path")
    print("A=温蒂，B=初雪：MATCH path=shortestpath((n:中文代号)-[r:`活跃领域`|" + print_type + "*]->(m:中文代号)) WHERE n.name=\"星熊\" AND m.name=\"塞雷娅\" RETURN path")
    print()

    print("灵活配置脚本，探索更灵活的查询结果吧！")
    print("注：1）适当设置LIMIT防止查询节点过大卡机（虽然目前约200干员影响不大）；2）查询未必有结果，可到Issue中留言。")

    print("- 执行完毕 -")
    return None


if __name__ == "__main__":
    add_operator_relation(load_entity="operator_entity.csv",
                          load_relation="operator_relation.csv",
                          load_cp="operator_cp.xlsx",
                          save_relation="operator_relation_cp.csv")
