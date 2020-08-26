import pypika
import pypika.functions

class QueryBuilder:
    def __init__(self, query):
        self.__query = query

    @property
    def subquery(self):
        return pypika.Query.from_(self.__query)

    @property
    def query(self):
        return self.__query

    def __to_string(self, query):
        return query.get_sql()

    def create(self, query, fork=True):
        return self.__class__(query.select('*'))

    def getitem(self, item):
        query = self.subquery
        if isinstance(item, slice):
            if item.start:
                query = query.offset(item.start)
            if item.stop:
                query = query.limit(item.stop)
        return self.create(query)

    @property
    def filter(self):
        return QueryFilter(self)

    @property
    def length(self):
        return self.__to_string(self.subquery.select(pypika.functions.Count('*')))

    def __str__(self):
        return self.__to_string(self.subquery.select('*'))


class QueryFilter:
    def __init__(self, query_builder):
        self.__query_builder = query_builder
    def __getattr__(self, name):
        return ColumnFilter(self.__query_builder, name)


class ColumnFilter:
    def __init__(self, query_builder, column_name):
        self.__query_builder = query_builder
        self.__column_name = column_name

    def __create(self, filter_clause):
        return self.__query_builder.create(self.__query_builder.subquery.where(filter_clause))

    def __ne__(self, other):
        return self.__create(pypika.Field(self.__column_name) != other)

    def __eq__(self, other):
        return self.__create(pypika.Field(self.__column_name) == other)
