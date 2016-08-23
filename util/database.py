# -*- coding: utf-8 -*-

import config

from tornado.log import app_log
from tornado.gen import coroutine
from tornado_mysql import pools, connections, cursors, converters

from .struct import Ignore
from .decorator import singleton


pools.DEBUG = config.Static.Debug

connections.DEFAULT_CHARSET = r'utf8'


@singleton
class MySQLPool():
    
    def __init__(self):
        
        options = {
                   r'max_idle_connections': config.Static.MySqlMaxIdleConn,
                   r'max_open_connections': config.Static.MySqlMaxOpenConn,
                   }
        
        self._m_pool = pools.Pool(
                                  {
                                   r'host':config.Static.MySqlMaster[0],
                                   r'port':config.Static.MySqlMaster[1],
                                   r'user':config.Static.MySqlUser,
                                   r'passwd':config.Static.MySqlPasswd,
                                   r'db':config.Static.MySqlName
                                   },
                                  **options
                                  )
        
        self._s_pool = pools.Pool(
                                  {
                                   r'host':config.Static.MySqlSlave[0],
                                   r'port':config.Static.MySqlSlave[1],
                                   r'user':config.Static.MySqlUser,
                                   r'passwd':config.Static.MySqlPasswd,
                                   r'db':config.Static.MySqlName
                                   },
                                  **options
                                  )
    
    @coroutine
    def get_client(self, readonly):
        
        result = None
        
        pool = self._s_pool if readonly else self._m_pool
        
        try:

            conn = yield pool._get_conn()
            
            result = DBClient(pool, conn, readonly)
            
        except Exception as err:
            
            pool._close_conn(conn)
            
            app_log.error(err)
            
        return result
    
    @coroutine
    def get_transaction(self):
        
        result = None
        
        pool = self._m_pool
        
        try:
        
            conn = yield pool._get_conn()
            
            yield conn.begin()
            
            result = DBTransaction(pool, conn)
            
        except Exception as err:
            
            pool._close_conn(conn)
            
            app_log.error(err)
            
        return result


class SQLQuery():
    
    class ReadOnly(Exception): pass
    
    SQL_LAST_INSERT_ID = r'SELECT last_insert_id() as insert_id;'
    
    @classmethod
    def Break(cls, msg=None):
        
        raise Ignore(msg)
    
    def __init__(self, readonly=False):
        
        self._readonly = readonly
    
    @classmethod
    def _format(cls, sqlstr, params):
        
        if(not isinstance(sqlstr, str)):
            sqlstr = str(sqlstr)
        
        style = type(params)
        
        if(style is dict):
            sqlstr = sqlstr.format(**params)
        elif(style is list):
            sqlstr = sqlstr.format(*params)
        
        return sqlstr
    
    @classmethod
    def safestr(cls, sqlstr):
        
        if(not isinstance(sqlstr, str)):
            sqlstr = str(sqlstr)
        
        return converters.escape_string(sqlstr)
    
    @classmethod
    def sqlwhere(cls, cond, sep=r' AND '):
        
        style = type(cond)
        
        if(style is dict):
            return sep.join(r"`{0:s}` = '{1:s}'".format(key, cls.safestr(val)) for key, val in cond.items())
        elif(style is list):
            return sep.join(r'({0:s})'.format(cls.sqlwhere(val)) for val in cond)
        else:
            return cond
    
    @property
    def readonly(self):
        
        return self._readonly
    
    def execute(self, sqlstr, params=None):
        
        app_log.debug(sqlstr)
    
    @coroutine
    def query(self, sqlstr, params=None):
        
        style = type(sqlstr)
        
        if(params):
            if(style is str):
                sqlstr = self._format(sqlstr, params)
            elif(style in (list, tuple)):
                for key, val in enumerate(sqlstr):
                    sqlstr[key] = self._format(val, params)
        
        result = yield self.execute(sqlstr)
        
        return result
    
    @coroutine
    def select(self, table, what='*', where=None, having=None, order=None, group=None, limit=None, offset=None, params=None, rowlock=False):
        
        sql_clauses = []
        
        sql_clauses.append(r'SELECT {0:s}'.format(what))
        sql_clauses.append(r'FROM {0:s}'.format(table))
        
        if(where):
            sql_clauses.append(r'WHERE {0:s}'.format(self.sqlwhere(where)))
        
        if(having):
            sql_clauses.append(r'HAVING {0:s}'.format(self.sqlwhere(having)))
        
        if(group):
            sql_clauses.append(r'GROUP BY {0:s}'.format(group))
        
        if(order):
            sql_clauses.append(r'ORDER BY {0:s}'.format(order))
        
        if(limit):
            sql_clauses.append(r'LIMIT {0:d}'.format(limit))
        
        if(offset):
            sql_clauses.append(r'OFFSET {0:d}'.format(offset))
        
        if(rowlock):
            sql_clauses.append((r'FOR UPDATE'))
        
        sqlstr = r'{0:s};'.format(r' '.join(sql_clauses))
        
        cursor = yield self.query(sqlstr, params)
        
        return cursor.fetchall() if cursor else None
    
    @coroutine
    def where(self, table, what='*', having=None, order=None, group=None, params=None, rowlock=False, **where):
        
        records = yield self.select(table, what, (where[r'where'] if r'where' in where else where), having, order, group, 1, params, rowlock)
        
        return records[0] if records else None
    
    @coroutine
    def count(self, table, **where):
        
        record = yield self.where(table, what=r'count(*) as total', **where)
        
        return record[r'total'] if record else 0
    
    @coroutine
    def insert(self, table, **fields):
        
        if(self._readonly):
            raise self.ReadOnly()
        
        keys = r', '.join(r'`{0:s}`'.format(val) for val in fields.keys())
        values = r', '.join(r"'{0:s}'".format(self.safestr(val)) for val in fields.values())
        
        sqlstr = r'INSERT INTO {0:s} ({1:s}) VALUES ({2:s});'.format(table, keys, values)
        
        cursors = yield self.query((sqlstr, self.SQL_LAST_INSERT_ID))
        
        if(len(cursors) == 2):
            result = cursors[1].fetchone()
            return result[r'insert_id'] if result else 0
        else:
            return 0
    
    @coroutine
    def duplicate_insert(self, table, fields1, fields2):
        
        if(self._readonly):
            raise self.ReadOnly()
        
        keys = r', '.join(r'`{0:s}`'.format(val) for val in fields1.keys())
        values = r', '.join(r"'{0:s}'".format(self.safestr(val)) for val in fields1.values())
        
        fields = r', '.join(r"`{0:s}` = '{1:s}'".format(key, self.safestr(val)) for key, val in fields2.items())
        
        sqlstr = r'INSERT INTO {0:s} ({1:s}) VALUES ({2:s}) ON DUPLICATE KEY UPDATE {3:s};'.format(table, keys, values, fields)
        
        cursors = yield self.query((sqlstr, self.SQL_LAST_INSERT_ID))
        
        if(len(cursors) == 2):
            result = cursors[1].fetchone()
            return result[r'insert_id'] if result else 0
        else:
            return 0
    
    @coroutine
    def multiple_insert(self, table, fields):
        
        if(self._readonly):
            raise self.ReadOnly()
        
        keys = None
        values = []
        
        for data in fields:
            
            if(keys):
                if(keys != data.keys()):
                    return 0
            else:
                keys = data.keys()
            
            values.append(r', '.join(r"'{0:s}'".format(self.safestr(val)) for val in data.values()))
        
        keys = r', '.join(r'`{0:s}`'.format(val) for val in keys)
        values = r', '.join(r'({0:s})'.format(val) for val in values)
        
        sqlstr = r'INSERT INTO {0:s} ({1:s}) VALUES {2:s};'.format(table, keys, values)
        
        cursors = yield self.query((sqlstr, self.SQL_LAST_INSERT_ID))
        
        if(len(cursors) == 2):
            result = cursors[1].fetchone()
            return result[r'insert_id'] if result else 0
        else:
            return 0
    
    @coroutine
    def update(self, tables, where, **fields):
        
        if(self._readonly):
            raise self.ReadOnly()
        
        fields = r', '.join(r"`{0:s}` = '{1:s}'".format(key, self.safestr(val)) for key, val in fields.items())
        
        sqlstr = r'UPDATE {0:s} SET {1:s} WHERE {2:s};'.format(tables, fields, self.sqlwhere(where))
        
        cursor = yield self.query(sqlstr)
        
        if(cursor):
            return cursor.rowcount
        else:
            return 0
    
    @coroutine
    def delete(self, table, where, using=None):
        
        if(self._readonly):
            raise self.ReadOnly()
        
        sql_clauses = []
        
        sql_clauses.append(r'DELETE FROM {0:s}'.format(table))
        
        if(using):
            sql_clauses.append(r'USING {0:s}'.format(using))
        
        sql_clauses.append(r'WHERE {0:s}'.format(self.sqlwhere(where)))
        
        sqlstr = r'{0:s};'.format(r' '.join(sql_clauses))
        
        cursor = yield self.query(sqlstr)
        
        if(cursor):
            return cursor.rowcount
        else:
            return 0


class DBClient(SQLQuery):
    
    def __init__(self, pool, conn, readonly):
        
        SQLQuery.__init__(self, readonly)
        
        self._pool = pool
        self._conn = conn
    
    def __enter__(self):
        
        return self
    
    def __exit__(self, *args):
        
        self._close()
        
        if(args[0] is Ignore):
            
            return True
            
        elif(args[1]):
            
            app_log.error(args[1])
            
            return True
    
    def __del__(self):
        
        self._close()
    
    @coroutine
    def execute(self, query, params=None):
        
        app_log.debug(query)
        
        result = None
        
        try:
            
            style = type(query)
            
            if(style is str):
                
                result = self._conn.cursor(cursors.DictCursor)
                
                yield result.execute(query, params)
                yield result.close()
                
            elif(style in (list, tuple)):
                
                result = []
                
                for sql in query:
                    
                    cursor = self._conn.cursor(cursors.DictCursor)
                    result.append(cursor)
                    
                    yield cursor.execute(sql, params)
                    yield cursor.close()
            
        except Exception as err:
            
            yield self._close()
            
            app_log.error(err)
            
            raise err
            
        return result
    
    def _close(self):
        
        if(self._pool and self._conn):
            
            self._pool._put_conn(self._conn)
            
            self._pool = self._conn = None


class DBTransaction(pools.Transaction, SQLQuery):
    
    def __init__(self, pool, conn):
        
        pools.Transaction.__init__(self, pool, conn)
        
        SQLQuery.__init__(self, False)
    
    def __enter__(self):
        
        return self
    
    def __exit__(self, *args):
        
        self.rollback()
        
        if(args[0] is Ignore):
            
            return True
            
        elif(args[1]):
            
            app_log.error(args[1])
            
            return True
    
    def __del__(self):
        
        self.rollback()
    
    @coroutine
    def execute(self, query, params=None):
        
        app_log.debug(query)
        
        result = None
        
        try:
            
            self._ensure_conn()
            
            style = type(query)
            
            if(style is str):
                
                result = self._conn.cursor(cursors.DictCursor)
                
                yield result.execute(query, params)
                yield result.close()
                
            elif(style in (list, tuple)):
                
                result = []
                
                for sql in query:
                    
                    cursor = self._conn.cursor(cursors.DictCursor)
                    result.append(cursor)
                    
                    yield cursor.execute(sql, params)
                    yield cursor.close()
            
        except Exception as err:
            
            yield self.rollback()
            
            app_log.error(err)
            
            raise err
            
        return result
    
    @coroutine
    def commit(self):
        
        if(self._pool and self._conn):
            
            yield self._conn.commit()
            
            self._close()
 
    @coroutine
    def rollback(self):
        
        if(self._pool and self._conn):
            
            yield self._conn.rollback()
            
            self._close()


safestr = SQLQuery.safestr
sqlwhere = SQLQuery.sqlwhere

