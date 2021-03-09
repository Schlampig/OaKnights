import json
from elasticsearch import Elasticsearch
from tqdm import tqdm


class ES(object):
    def __init__(self, source="es_data.json", index_name="es_base", top_k=3, re_build=False):
        """
        初始化ElasticSearch类
        :param source: 来自prepare_data.py的原始待入库（三元组）数据
        :param index_name: ElasticSearch索引对象名称，默认es_base
        :param top_k: ES搜索返回前K个答案
        :param re_build: 是否清空并入库新数据，默认为False
        """
        self.lst, self.lst_person = self.__load__(source)
        self.index_name = index_name
        self.top_k = top_k
        self.es = Elasticsearch([{"host": "localhost", "port": 7777}])  # port处填写你在yml文件自设的ElasticSearch服务接口地址
        if re_build:
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
            self.es.indices.create(index=self.index_name, ignore=400)
            self.es = self.es_build()

    @staticmethod
    def __load__(source):
        """
        载入来自prepare_data.py的原始待入库（三元组）数据
        :param source: string / dictionary, 若为string则读取文件，若为dictionary直接处理
        :return: list, list, lst为入库词条（三元组）列表，lst_person为干员中文代码列表
        """
        lst, lst_person = None, None
        if isinstance(source, dict):
            lst, lst_person = source.get("entry", None), source.get("people", None)
        if isinstance(source, str) and source.endswith(".json"):
            with open(source, "r") as f:
                d = json.load(f)
                lst, lst_person = d.get("entry", None), d.get("people", None)
        if lst is None or lst_person is None:
            raise KeyError("[ERROR] Fail to load data...")
        return lst, lst_person

    def es_build(self):
        """
        将build_answer.py生成好的数据插入ElesticSearch数据库
        :param lst: list, lst=[d_1, d_2, ...], where d_i = {"text": string, "id": string}
        :return: Boolean (True for successfully update es, otherwise False)
        """
        # initialize es and inserting format
        self.es.delete_by_query(index=self.index_name, body={"query": {"bool": {"should": {"match_all": {}}}}},
                                ignore=400)
        self.es.indices.create(index=self.index_name, ignore=400)
        self.es.indices.refresh(index=self.index_name)
        # use ik_max_word or ik_smart to tokenization
        mapping = {
            "properties": {
                "person": {
                    "type": "text"
                },
                "prefix": {
                    "type": "text",
                },
                "content": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "search_analyzer": "ik_max_word"
                }
            }
        }
        self.es.indices.put_mapping(index=self.index_name, body=mapping)
        # insert data
        for answer in tqdm(self.lst):
            d_body = {"person": answer.get("person"),
                      "prefix": answer.get("prefix"),
                      "content": answer.get("content")}
            self.es.index(index=self.index_name, body=d_body)
        self.es.indices.refresh(index=self.index_name)
        if self.es.indices.exists(index=self.index_name):
            print("Success to build ES.")
        else:
            print("[ERROR] Failed to build ES.")
        return self.es

    def es_search(self, query, lst_person):
        """
        在ElesticSearch数据库中找寻最匹配的前k个答案的搜索模式，可自定义rule
        :param query: string, 想要搜索的问题
        :param lst_person: list, 问题中关联的干员中文代号（即干员名）
        :return: es-based json-like data structure, the eligible result
        """
        # define searching rules
        if len(lst_person) > 0:  # if recognize operators in query, searching correlated to operator code
            lst_should = [{"match": {"person": person}} for person in lst_person]
            rule = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"content": query}},
                            {"bool": {"should": lst_should}}
                        ]
                    }
                }
            }
        else:
            rule = {
                "query": {
                    "match": {
                        "content": query
                    }
                }
            }
        # search for candidates
        result = self.es.search(index=self.index_name, size=self.top_k, body=rule)
        return result

    def run(self, query):
        """
        根据输入的query在ElesticSearch数据库中找寻最匹配的前k个answer
        :param query: string, 想要搜索的问题
        :return: lst_res = [answer_1, answer_2, ...], 前k个答案
        """
        # find people mentioned in query
        lst_p = [person for person in self.lst_person if person in query]
        # search the database
        es_res = self.es_search(query, lst_p)
        # return matched results
        lst_res = list()
        for x in es_res.get("hits", {}).get("hits", []):
            res = x.get("_source").get("prefix") + x.get("_source").get("content")
            if len(res) > 0:
                lst_res.append(res)
        return lst_res


if __name__ == "__main__":
    # 测试/入库用
    es_re = ES(top_k=7, re_build=False)  # 注意这里第一次设True让数据入库，后续可改为False不必重复入库占用时间
    answers = es_re.run("泰拉这片大地的苦难何时结束")
    for ans in answers:
        print(ans)
        print()
