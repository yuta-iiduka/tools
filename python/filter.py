import json, datetime
from sqlalchemy import and_, or_, not_, desc
from controller_sticky import app, db, User, Task, transaction

# import inspect
# from your_application import db
# from your_application.models import *

# def get_all_models():
#     models = []
#     for name, obj in inspect.getmembers(db.Model):
#         if inspect.isclass(obj) and issubclass(obj, db.Model) and obj != db.Model:
#             models.append(obj)
#     return models

# # 使用例
# models = get_all_models()
# for model in models:
#     print(model.__name__)


# class DBWrapper(User):

#     @transaction
#     def __init__(self):
#         self.users = db.session.query(User).all()
#         print(self.users)
        
# class Comparision(Enum):
#         "EQUAL":"equal","NOTEQUAL":"not_equal",
#         "BIGGER":"bigger","SMALLER":"smaller",
#         "EQUAL_BIGGER":"equal_bigger","EQUAL_SMALLER":"equal_smaller",
#         "BEFORE":"before","AFTER":"after",
#         "EQUAL_BEFORE":"equal_before","EQUAL_AFTER":"equal_after",
#         "INCLUDE":"include","NOT_INCLUDE":"not_include"

class Filter():
    """ データをフィルタするクラス
    
    属性:
    condition:辞書型のフィルタ条件を保持するプロパティ
    data:フィルタ対象の辞書型データリスト
    result:フィルタ後の辞書型データリスト
    """
    COMPARISION = {
        "EQUAL":"equal","NOTEQUAL":"not_equal",
        "BIGGER":"bigger","SMALLER":"smaller",
        "EQUAL_BIGGER":"equal_bigger","EQUAL_SMALLER":"equal_smaller",
        "BEFORE":"before","AFTER":"after",
        "EQUAL_BEFORE":"equal_before","EQUAL_AFTER":"equal_after",
        "INCLUDE":"include","NOT_INCLUDE":"not_include"
    }
    WORD = {"FIELD":"field","VALUE":"value","COMPARISION":"comparision"}
    DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"
    PAGEDATA = 2

    def __init__(self,condition=None,data=None):

        self._condition = condition
        self._data = data
        self._result = None
        self.obj = UniqeDict
        self.order_by = None
        self.desc     = False

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self,data):
        self._data = data

    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self,condition):
        self._condition = condition

    @property
    def result(self):
        return self._result
    
    @result.setter
    def result(self,result):
        self._result = result

    @property
    def fields(self):
        if any(self.result):
            return self.result[0].keys()
        return ()
    
    @property
    def order_data(self):
        if self.order_by is not None:
            if self.desc:
                return sorted(self.data, key=lambda x:x[self.order_by],reverse=True)
            else:
                return sorted(self.data, key=lambda x:x[self.order_by])
        return self.data

    def _and(self,condition):
        result = self.order_data
        for con in condition:
            field = con[Filter.WORD["FIELD"]]
            value = con[Filter.WORD["VALUE"]]
            comparision = con[Filter.WORD["COMPARISION"]]
            result = self._filter(result,field,value,comparision)
        return result
    
    def _or(self,condition):
        result = []
        for con in condition:
            result.extend(self._and(con))
        return result
    
    def search(self):
        """ データを結果として保持し、返却する関数
        """
        self.result = self.unique(self._or(self.condition))
        return self.result

    def unique(self,data):
        """ ハッシュ可能オブジェクトにdataを格納する関数

        """ 
        l = []
        s = set()
        if type(data) == type(dict()):
            for d in data:
                    s.add( self.make_data_unique(data))
                
            for d in s:
                if d is not None:
                    l.append(d.data)
            return l
        
        else:
            return data
    
    # データの種類に合わせてユニークなデータ型を再定義する
    def make_data_unique(self,data):
        """ ハッシュ可能オブジェクトにdataを格納する関数

        ハッシュ可能オブジェクトはdataプロパティを持たなければならない。
        """
        udata = type(self.obj)(data)
        if hasattr(udata,"data"):
            return udata
        return None
    
    # データの種類に合わせてオーバライドする関数
    def _filter(self,result,field,value,comparision):
        return list(filter(lambda data: self.filter_logic(
                    data[field] if type(data) == type({}) else data.data[field],
                    value,
                    comparision
                    ), result)
                )
    
    def filter_logic(self,data_value,value,comparision):
        result = False
        d = data_value
        if comparision == Filter.COMPARISION["EQUAL"]:
            result = self._equal(d,value)
        elif comparision == Filter.COMPARISION["NOTEQUAL"]:
            result = self._not_equal(d,value)
        elif comparision == Filter.COMPARISION["BIGGER"]:
            result = self._bigger(d,value)
        elif comparision == Filter.COMPARISION["SMALLER"]:
            result = self._smaller(d,value)
        elif comparision == Filter.COMPARISION["EQUAL_BIGGER"]:
            result = self._equal_bigger(d,value)
        elif comparision == Filter.COMPARISION["EQUAL_SMALLER"]:
            result = self._equal_smaller(d,value)
        elif comparision == Filter.COMPARISION["BEFORE"]:
            result = self._before(d,value)
        elif comparision == Filter.COMPARISION["AFTER"]:
            result = self._after(d,value)
        elif comparision == Filter.COMPARISION["EQUAL_BEFORE"]:
            result = self._equal_before(d,value)
        elif comparision == Filter.COMPARISION["EQUAL_AFTER"]:
            result = self._equal_after(d,value)
        elif comparision == Filter.COMPARISION["INCLUDE"]:
            result = self._include(d,value)
        elif comparision == Filter.COMPARISION["NOT_INCLUDE"]:
            result = self._not_include(d,value)
        else:
            pass
        return result
    
    def _equal(self,data_value,value):
        return data_value == value
    
    def _not_equal(self,data_value,value):
        return data_value != value

    def _bigger(self,data_value,value):
        return data_value > value
    
    def _smaller(self,data_value,value):
        return data_value < value
    
    def _equal_bigger(self,data_value,value):
        return data_value >= value
    
    def _equal_smaller(self,data_value,value):
        return data_value <= value
    
    def _before(self,data_value,value):
        return datetime.datetime.strptime(data_value,Filter.DATETIME_FORMAT) < datetime.datetime.strptime(value) 

    def _after(self,data_value,value):
        return datetime.datetime.strptime(data_value,Filter.DATETIME_FORMAT) > datetime.datetime.strptime(value) 

    def _equal_before(self,data_value,value):
        return datetime.datetime.strptime(data_value,Filter.DATETIME_FORMAT) <= datetime.datetime.strptime(value) 

    def _equal_after(self,data_value,value):
        return datetime.datetime.strptime(data_value,Filter.DATETIME_FORMAT) >= datetime.datetime.strptime(value) 

    def _include(self,data_value,value):
        return value in data_value

    def _not_include(self,data_value,value):
        return value not in data_value


class DBFilter(Filter):
    """ SQLAlchemyのデータフィルターを自動生成するクラス

    属性：
    condition:フィルター条件辞書型データ -- {field,value,comparision}
    data:フィルター対象データ -- db.session.query()
    trans:カラム名とカラムオブジェクトの変換リスト -- {"id":Table.id,"name":Table.name,...}
    result:クエリ結果 -- [<Result1>,<Result2>,...]
    
    利用方法：
    1. condition,data,transを設定する
    2. search(),first(),get()でクエリを発行する
    """
    def __init__(self,condition=None,data=None):

        super().__init__(condition,data)
        self.trans = {}

    @property
    @transaction
    def fields(self):
        """ クエリ結果のカラム名の一覧データ（不可変）
        """
        return () if not any(self.result) else self.result[0]._fields
    
    @property
    @transaction
    def dict(self):
        """ クエリ結果の辞書型形式のデータ
        """
        l = []
        if any(self.result):
            for r in self.result:
                d = {}
                for f in self.fields:
                    d[f] = getattr(r,f)
                l.append(d)
        return l


    def _and(self,condition):
        result = []
        for con in condition:
            field = con[Filter.WORD["FIELD"]]
            value = con[Filter.WORD["VALUE"]]
            comparision = con[Filter.WORD["COMPARISION"]]
            result = self._filter(result,field,value,comparision)
        return and_(*result)
    
    def _or(self,condition):
        result = []
        for con in condition:
            result.append(self._and(con))
        return or_(*result)
    
    def _filter(self,result,field,value,comparision):
        if field in self.trans:
            result.append(self.filter_logic(self.trans[field],value,comparision))
        else:
            print("フィールド名「{}」に対応するオブジェクトの設定ができていません。".format(field))
        return result
    
    def _not_equal(self,data_value,value):
        return not_(super()._equal(data_value,value))
    
    def _before(self, data_value, value):
        return data_value < value
    
    def _after(self, data_value, value):
        return data_value > value
    
    def _equal_before(self, data_value, value):
        return data_value <= value
    
    def _equal_after(self, data_value, value):
        return data_value >= value

    def _include(self, data_value, value):
        return data_value.like("%{}%".format(value))
    
    def _not_include(self, data_value, value):
        return not_(data_value.like("%{}%".format(value)))

    @property
    def order_data(self):
        if self.order_by is not None:
            if self.desc :
                return self.data.order_by(desc(self.order_by))
            else:
                return  self.data.order_by(self.order_by)
        return self.data

    @transaction
    def search(self):
        """ フィルター設定を反映したクエリを発行し全件取得する
        """
        self.result = self.order_data.filter(self._or(self.condition)).all()
        return self.result
    
    @transaction
    def paginate(self,index):
        """ フィルター設定を反映したクエリを発行しページネーションを取得する
        """
        self.result = self.order_data.filter(self._or(self.condition)).paginate(page=index,per_page=Filter.PAGEDATA,error_out=False).items
        return self.result

    @transaction
    def first(self):
        """ フィルター設定を反映したクエリを発行し一件取得する
        """
        self.result = self.order_data.filter(self._or(self.condition)).first()
        return self.result
    
    @transaction
    def get(self,n):
        """ フィルター設定を反映したクエリを発行しn件取得する
        """
        self.result = self.order_data.filter(self._or(self.condition)).limit(n).all()
        return self.result

class UniqeDict():
    """ ハッシュ可能オブジェクト
    
    dict:内部に辞書型をもつ。
    辞書型データの各要素と値が完全に一致している場合、同一のものとみなす。
    つまりセット型で重複せずに辞書データを格納することが可能
    例）
    d1 = UniqeDict({"id":1,"name":"aaa"})
    d2 = UniqeDict({"id":2,"name":"bbb"})
    d3 = UniqeDict({"id":1,"name":"aaa"})
    上記の例だと、「d1 != d2, d1 == d3」となる
    """
    def __init__(self,dict):
        self._dict = dict

    def __hash__(self):
        return hash(json.dumps(self._dict))

    def __eq__(self, other):
        is_equal = True
        for k,v in other.items:
            if self._dict[k] != v:
                is_equal = False
        return is_equal
        
    @property
    def values(self):
        return self._dict.values()
    
    @property
    def keys(self):
        return self._dict.keys()
    
    @property
    def items(self):
        return self._dict.items()
    
    @property
    def dict(self):
        """内部データのゲッター
        """
        return self._dict
    
    @dict.setter
    def dict(self,dict):
        """内部データのセッター
        """
        self._dict = dict

    @property
    def data(self):
        """内部データ読み取り専用プロパティ(self.dictと同じ)
        """
        return self._dict


@transaction
def sample():
    # print({"id":1,"name":"aaa"}.items())
    # d1 = UniqeDict({"id":1,"name":"aaa"})
    # d2 = UniqeDict({"id":2,"name":"bbb"})
    # d3 = UniqeDict({"id":3,"name":"ccc"})
    # d4 = UniqeDict({"id":4,"name":"ddd"})
    # d5 = UniqeDict({"id":5,"name":"eee"})

    d1 = {"id":1,"name":"aaa"}
    d2 = {"id":2,"name":"bbb"}
    d3 = {"id":3,"name":"ccc"}
    d4 = {"id":4,"name":"ddd"}
    d5 = {"id":5,"name":"eee"}


    f = Filter()
    f.data = [d1,d2,d3,d4,d5]
    f.condition = [
        [
            {"field":"name","value":"ddd","comparision":"equal"},
            {"field":"id","value":2,"comparision":"bigger"},
        ],
        [
            {"field":"name","value":"aaa","comparision":"equal"},
        ]
    ]
    f.order_by = "id"
    f.desc = True
    result = f.search()
    print(result)

    # with app.app_context():
    dbf = DBFilter()
    dbf.data = db.session.query(User.id,User.username,Task.explanation).join(Task,User.id==Task.user_id)
    dbf.trans = {"id":User.id, "username":User.username, "explanation":Task.explanation}
    dbf.condition = [
        [
            {"field":"id","value":1,"comparision":"bigger"},{"field":"id","value":3,"comparision":"equal_smaller"},
        ],
        [
            {"field":"username","value":"ff","comparision":"include"},
        ]
    ]
    dbf.order_by = User.id
    dbf.desc = True

    # print(dbf.search())
    # print(dbf.dict)
    print(dbf.paginate(2))

if __name__ == "__main__":
    sample()

