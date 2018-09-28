# -*- coding:utf-8 -*-
import MySQLdb
import os
import sys
from flask import make_response
from flask import jsonify
from app import app
from flask import request
from app.database_config import *
from werkzeug.utils import secure_filename

# 狗跨域
def cors_response(res):
    response = make_response(jsonify(res))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

def LongToInt(value):
    assert isinstance(value, (int, long))
    return int(value & sys.maxint)

@app.route('/submitRecord', methods=['POST'])
def submitRecord():
    content = request.values.get("content")
    showType = request.values.get("showType")
    if content:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        # 入库
        sql = 'insert into record_list (content,showType) VALUES (%s,%s)'
        dbc.execute(sql, (content, showType))
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '添加成功'})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '添加失败'})
        return response