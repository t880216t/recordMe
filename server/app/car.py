# -*- coding:utf-8 -*-
import json

import MySQLdb
import os
import time

import sys

import xlrd
from flask import make_response
from flask import render_template, flash, redirect, jsonify, Response
from app import app
from threading import Thread
from flask import request
from bs4 import BeautifulSoup
from app.database_config import *

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

@app.route('/addcar', methods=['POST'])
def addcar():
    carinfo = request.json.get("carinfo")
    imageIds = request.json.get("imageIds")
    reports = request.json.get("reports")

    title = carinfo["title"]
    price = carinfo["price"]
    oldPrice = carinfo["oldPrice"]
    gongLi = carinfo["gongLi"]
    city = carinfo["city"]
    dang = carinfo["dang"]
    description = carinfo["desc"]
    cartype = carinfo["cartype"]
    carOut = carinfo["carOut"]
    carTime = carinfo["carTime"]
    pailiang = carinfo["pailiang"]
    isPay = carinfo["isPay"]
    firstPay = carinfo["firstPay"]
    payTime = carinfo["payTime"]
    mPay = carinfo["mPay"]
    imageIds = str(imageIds)
    reports = json.dumps(reports)

    # 连接
    db = MySQLdb.connect(database_host,database_username,database_password,database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'insert into car_list (title,price,oldPrice,gongLi,city,dang,description,cartype,carOut,carTime,pailiang,isPay,firstPay,payTime,mPay,imageIds,reports,isSaled,isDelete) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,0)'

    # test = sql%(title,price,oldPrice,gongLi,dang,description,cartype,carOut,carTime,pailiang,isPay,firstPay,payTime,mPay,imageIds,reports)
    # print(test)
    dbc.execute(sql, (title,price,oldPrice,gongLi,city,dang,description,cartype,carOut,carTime,pailiang,isPay,firstPay,payTime,mPay,imageIds,reports))

    db.commit()
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '上传成功'})
    return response


from werkzeug.utils import secure_filename
import os

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploadimage', methods=['POST'])
def uploadimage():
    upload_file = request.files["file"]
    if upload_file:
        if allowed_file(upload_file.filename):
            # 连接
            db = MySQLdb.connect(database_host,database_username,database_password,database1)
            dbc = db.cursor()
            # 编码问题
            db.set_character_set('utf8')
            dbc.execute('SET NAMES utf8;')
            dbc.execute('SET CHARACTER SET utf8;')
            dbc.execute('SET character_set_connection=utf8;')

            filename = secure_filename(upload_file.filename)
            imageId = int(round(time.time() * 1000))
            #保存文件
            upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            imageURL = "static/uploads/"+filename
            sql = 'insert into car_image (imageId,imageURL) VALUES (%s,%s)'
            dbc.execute(sql, (imageId,imageURL))
            db.commit()
            dbc.close()
            db.close()

            response = cors_response({'code': 0, 'imageId': imageId})
            return response
        else:
            response = cors_response({'code': 10002, 'msg': '不支持的文件格式'})
            return response
    else:
        response = cors_response({'code': 10001, 'msg': '上传失败'})
        return response

@app.route('/searchlist', methods=['POST'])
def search_list():
    try:
        carType = request.json.get("carType")
        salPrice = request.json.get("salPrice")
        paiXuType = request.json.get("paiXuType")
        carTitle = request.json.get("carTitle")

    except:
        carType = request.values.get("carType")
        salPrice = request.values.get("salPrice")
        paiXuType = request.values.get("paiXuType")
        carTitle = request.values.get("carTitle")

    if carType == u"全部车型":
        carType = u""
    if salPrice == u"不限":
        salPrice = u""
    if paiXuType == u"默认排序":
        paiXuType = u""

    sql = 'select * from car_list where isDelete = 0 '
    if carType != "" and carType != None:
        l1 = 'cartype = "%s"'%carType
        sql = 'select * from car_list where isDelete = 0 AND '+l1
    if salPrice != "" and salPrice != None:

        l2 = ''
        if salPrice == u'3万以下':
            l2 = ' and price <= 3 '
        if salPrice == u'3-5万':
            l2 = ' and price >= 3 and price <= 5 '
        if salPrice == u'5-10万':
            l2 = ' and price >= 5 and price <= 10 '
        if salPrice == u'10-15万':
            l2 = ' and price >= 10 and price <= 15 '
        if salPrice == u'15-20万':
            l2 = ' and price >= 15 and price <= 20 '
        if salPrice == u'20-30万':
            l2 = ' and price >= 20 and price <= 30 '
        if salPrice == u'30万以上':
            l2 = ' and price >= 30'
        if carType == u"":
            sql = 'select * from car_list where isDelete = 0 AND '
            l2 = l2[4:len(l2)]
        sql = sql + l2
    if paiXuType != "" and paiXuType != None:
        l3 = ''
        if paiXuType == u'最新发布':
            l3 = ' order by addTime desc'
        if paiXuType == u'价格最低':
            l3 = ' ORDER BY price DESC '
        if paiXuType == u'价格最高':
            l3 = ' ORDER BY price ASC '
        if paiXuType == u'最短里程':
            l3 = ' ORDER BY gongLi ASC '
        sql = sql + l3

    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    if carTitle != "" and carTitle != None:
        carTitle = carTitle.replace('>','')
        carTitle = carTitle.replace('<','')
        carTitle = carTitle.replace('=','')
        carTitle = carTitle.replace('or','')
        carTitle = carTitle.replace('and','')
        carTitle = carTitle.replace('-','')
        sql = 'select * from car_list where isDelete = 0 and title like "%%%s%%"'%carTitle
        dbc.execute(sql)
    else:
        dbc.execute(sql)
    car_list = dbc.fetchall()
    if car_list is None or len(car_list) < 1:
        response = cors_response({'code': 10001, 'msg': '还没有车辆信息'})
        return response
    result = []
    for obj in car_list:
        imageIds = obj[16]
        imageIds = imageIds.replace("[","")
        imageIds = imageIds.replace("]","")
        imageIds = imageIds.replace("L","")
        imageIds = imageIds.split(',')
        first_image = imageIds[0]
        sql = 'select imageURL from car_image where imageId = %s'%first_image
        dbc.execute(sql)
        imageData = dbc.fetchone()
        if imageData is not None:
            imageURL = 'http://192.168.0.108:5000/'+imageData[0]
        else:
            imageURL = 'http://192.168.0.108:5000/'+'static/uploads/no_image.jpg'

        result.append({"id": obj[0],
                       "title": obj[1],
                       "carTime": obj[10],
                       "gongLi": obj[4],
                       "price": obj[2],
                       "firstPay": obj[13],
                       "imageURL": imageURL,
                       })
    db.commit()
    dbc.close()
    db.close()
    response = cors_response({"code": 0, "content": result})
    return response

@app.route('/getdetail', methods=['POST'])
def get_detail():
    try:
        carid = request.json.get("carid")
    except:
        carid = request.values.get("carid")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select id,title,price,oldPrice,gongLi,city,dang,carOut,carTime,pailiang,isPay,firstPay,mPay,imageIds,isSaled,isDelete from car_list where id = %s '%carid
    dbc.execute(sql)
    car_data = dbc.fetchone()

    if car_data is None:
        response = cors_response({'code': 0, 'msg': '还没有车辆信息'})
        return response
    car_info = car_data
    imageIds = car_info[13]
    imageIds = imageIds.replace("[", "(")
    imageIds = imageIds.replace("]", ")")
    imageIds = imageIds.replace("L", "")
    sql = 'select imageURL from car_image where imageId in %s' % imageIds
    dbc.execute(sql)
    imageData = dbc.fetchall()
    imageURLs = []
    for obj in imageData:
        imageURLs.append('http://192.168.0.108:5000/'+obj[0])

    result = []
    result.append({"id": car_info[0],
                   "title": car_info[1],
                   "price": car_info[2],
                   "oldPrice": car_info[3],
                   "gongLi": car_info[4],
                   "city": car_info[5],
                   "dang": car_info[6],
                   "carOut": car_info[7],
                   "carTime": car_info[8],
                   "pailiang": car_info[9],
                   "isPay": car_info[10],
                   "firstPay": car_info[11],
                   "mPay": car_info[12],
                   "isSaled": car_info[14],
                   "isDelete": car_info[15],
                   "imageURLs": imageURLs,
                   })
    db.commit()
    dbc.close()
    db.close()
    response = cors_response({"code": 0, "content": result})
    return response

@app.route('/getreport', methods=['POST'])
def get_report():
    try:
        carid = request.json.get("carid")
    except:
        carid = request.values.get("carid")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select id,title,description,reports from car_list where id = %s '%carid
    dbc.execute(sql)
    car_data = dbc.fetchone()

    if car_data is None:
        response = cors_response({'code': 0, 'msg': '还没有车辆信息'})
        return response
    car_info = car_data
    result = []
    result.append({"id": car_info[0],
                   "title": car_info[1],
                   "description": car_info[2],
                   "reports": json.loads(car_info[3]),
                   })
    db.commit()
    dbc.close()
    db.close()
    response = cors_response({"code": 0, "content": result})
    return response

@app.route('/getfenqi', methods=['POST'])
def get_fenqi():
    try:
        carid = request.json.get("carid")
    except:
        carid = request.values.get("carid")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select id,title,oldPrice,firstPay,mPay,payTime from car_list where id = %s '%carid
    dbc.execute(sql)
    car_data = dbc.fetchone()

    if car_data is None:
        response = cors_response({'code': 0, 'msg': '还没有车辆信息'})
        return response
    car_info = car_data
    result = []
    result.append({"id": car_info[0],
                   "title": car_info[1],
                   "oldPrice": car_info[2],
                   "firstPay": car_info[3],
                   "mPay": car_info[4],
                   "payTime": car_info[5],

                   })
    db.commit()
    dbc.close()
    db.close()
    response = cors_response({"code": 0, "content": result})
    return response

@app.route('/deleteCar', methods=['POST'])
def delete_car():
    try:
        carid = request.json.get("carid")
    except:
        carid = request.values.get("carid")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'update car_list set isDelete = 1 where id = %s'
    state = dbc.execute(sql, (carid,))
    db.commit()

    if state:
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '下架成功'})
        return response
    else:
        dbc.close()
        db.close()
        response = cors_response({'code': 10001, 'msg': '下架失败'})
        return response

@app.route('/unableCar', methods=['POST'])
def unable_car():
    try:
        carid = request.json.get("carid")
    except:
        carid = request.values.get("carid")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'update car_list set isSaled = 1 where id = %s'
    state = dbc.execute(sql, (carid,))
    db.commit()

    if state:
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '下架成功'})
        return response
    else:
        dbc.close()
        db.close()
        response = cors_response({'code': 10001, 'msg': '下架失败'})
        return response