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
            if relation_t2h != "无":
                r_now = pd.DataFrame({":START_ID(node)": [tail_id], ":END_ID(node)": [head_id],
                                      ":TYPE": [relation_t2h], "name": [relation_t2h]})
                df_relation = df_relation.append(r_now)
    # 存储新关系
    df_relation.to_csv(save_relation, index=False, encoding="utf-8-sig")
    print("- 执行完毕 -")
    return None


if __name__ == "__main__":
    add_operator_relation(load_entity="operator_entity.csv",
                          load_relation="operator_relation.csv",
                          load_cp="operator_cp.xlsx",
                          save_relation="operator_relation_cp.csv")
