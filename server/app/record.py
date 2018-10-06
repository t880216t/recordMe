# -*- coding:utf-8 -*-
import MySQLdb
import os, time
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
    attachmentIds = request.values.get("attachmentIds")
    lat = request.values.get("lat")
    lon = request.values.get("lon")
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
        sql = 'insert into record_list (content,showType,attachmentIds,lat,lon) VALUES (%s,%s,%s,%s,%s)'
        dbc.execute(sql, (content, showType, attachmentIds, lat, lon))
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '添加成功'})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '添加失败'})
        return response


@app.route('/uploadRecordImages', methods=['POST'])
def uploadRecordImages():
    upload_files = request.files.getlist('file')
    if upload_files:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        attachment_ids = []
        for upload_file in upload_files:
            filename = secure_filename(upload_file.filename)
            t = int(round(time.time() * 1000))
            if filename:
                filename = str(t) + filename
            else:
                filename = str(t) + '.png'
            # 保存文件
            upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            # 入库
            sql = 'insert into attachment (file_name,url) VALUES (%s,%s)'
            dbc.execute(sql, (filename, '/static/uploads/' + filename))
            db.commit()
            # 取id
            getId = 'SELECT LAST_INSERT_ID()'
            dbc.execute(getId)
            ids = dbc.fetchone()
            attachment_id = ids[0]
            attachment_ids.append(str(attachment_id))
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '上传成功', 'content': {'attachment_ids': attachment_ids}})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '上传失败'})
        return response


@app.route("/getRecordList", methods=["POST", "GET"])
def getRecordList():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    resultList = []
    sql = "SELECT * FROM record_list ORDER BY addTime DESC "
    dbc.execute(sql, ())
    queryList = dbc.fetchall()
    if len(queryList) > 0:
        for item in queryList:
            imageUrls = []
            if item[5]:
                ids = item[5].replace("[", "")
                ids = ids.replace("]", "")
                atSql = 'select url from attachment where id in (%s)' % ids
                dbc.execute(atSql)
                urlData = dbc.fetchall()
                if len(urlData) > 0:
                    for urlItem in urlData:
                        imageUrls.append('http://192.168.0.106:5000'+urlItem[0])
            resultList.append({
                "id": item[0],
                "content": item[1],
                "lat": item[2],
                "lon": item[3],
                "add_time": item[6].strftime('%Y-%m-%d'),
                "imageUrls": imageUrls,
            })
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '获取成功', 'content': resultList})
    return response


@app.route("/getRecordDetail", methods=["POST"])
def getRecordDetail():
    detailId = request.values.get("detailId")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select * from record_list where id = %s '
    dbc.execute(sql, (detailId,))
    data = dbc.fetchone()
    if data is None:
        response = cors_response({'code': 0, 'msg': '还没有信息'})
        return response
    imageUrls = []
    if data[5]:
        ids = data[5].replace("[", "")
        ids = ids.replace("]", "")
        atSql = 'select url from attachment where id in (%s)' % ids
        dbc.execute(atSql)
        urlData = dbc.fetchall()
        if len(urlData) > 0:
            for urlItem in urlData:
                imageUrls.append('http://192.168.0.106:5000'+urlItem[0])
    result = {
        "id":data[0],
        "content": data[1],
        "lat": data[2],
        "lon": data[3],
        "add_time": data[6].strftime('%Y-%m-%d'),
        "imageUrls": imageUrls,
    }
    db.commit()
    dbc.close()
    db.close()
    response = cors_response({"code": 0, "content": result})
    return response
