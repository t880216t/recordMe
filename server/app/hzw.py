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

@app.route('/getVideoList', methods=['GET'])
def getVideoList():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    gfvideoList = []
    fwvideoList = []

    sql = 'select * from video_list where video_type = "原画" ORDER by add_time DESC'
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) > 0:
        for item in queryList:
            #预览图
            image_url_sql = 'select url from attachment where id = %s'
            dbc.execute(image_url_sql, (item[2],))
            image_url = dbc.fetchone()[0]
            #评论数
            repaly_count_sql = 'select id from pinglun_list where ptype = "video" and pid = %s '%item[2]
            dbc.execute(repaly_count_sql)
            repalyCountList = dbc.fetchall()
            remark_count = len(repalyCountList)
            gfvideoList.append({
                "id": item[0],
                "title": item[1],
                "img": "http://orion-c.top/app"+image_url,
                'remark':remark_count,
                "play_count":item[6],
            })
    sql = 'select * from video_list  where video_type = "番外" ORDER by add_time DESC'
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) > 0:
        for item in queryList:
            image_url_sql = 'select url from attachment where id = %s'
            dbc.execute(image_url_sql, (item[2],))
            image_url = dbc.fetchone()[0]
            repaly_count_sql = 'select id from pinglun_list where ptype = "video" and pid = %s ' % item[2]
            dbc.execute(repaly_count_sql)
            repalyCountList = dbc.fetchall()
            remark_count = len(repalyCountList)
            fwvideoList.append({
                "id": item[0],
                "title": item[1],
                "img": "http://orion-c.top/app"+image_url,
                'remark': remark_count,
                "play_count": item[6],
            })

    result = {
        "gan": True,
        "gfvideoList": gfvideoList,
        "fwvideoList":fwvideoList,
    }
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getVideoDetail', methods=['GET'])
def getVideoDetail():
    id = request.values.get("detailId")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'select * from video_list where id = %s'
    dbc.execute(sql,(id,))
    detail = dbc.fetchone()
    atSql = 'select url from attachment where id = %s'
    dbc.execute(atSql, (detail[3],))
    url = dbc.fetchone()
    # 评论
    repaly_count_sql = 'select * from pinglun_list where ptype = "video" and pid = %s and status = "1" ' % detail[0]
    dbc.execute(repaly_count_sql)
    repalyCountList = dbc.fetchall()
    replayList = []
    if len(repalyCountList) > 0 :
        has_repaly = True
        for i in range (0,len(repalyCountList)):
            replayList.append({
                "id":repalyCountList[i][0],
                "avantar": repalyCountList[i][3],
                "user_name": repalyCountList[i][4],
                "replay_time": repalyCountList[i][6],
                "lou": len(repalyCountList) - i,
                "replay_desc": repalyCountList[i][5],
            })
    else:
        has_repaly = False

    result = {
        "title": detail[1],
        "video_url": "http://orion-c.top/app"+url[0],
        "play_count": detail[6],
        "add_time":  detail[4].strftime('%Y-%m-%d'),
        "has_replay_list": has_repaly,
        "replay_list":replayList ,
    }
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getPicList', methods=['GET'])
def getPicList():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    gfpicList = []
    fwpicList = []

    sql = 'select * from pic_list ORDER by add_time DESC'
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) > 0:
        for item in queryList:
            atSql = 'select url from attachment where id in (%s)'%item[2]
            dbc.execute(atSql)
            imageUrl = dbc.fetchone()
            # print urlList
            # newUrlList = []
            # for image_item in urlList:
            #     newUrlList.append(image_item[0])
            gfpicList.append({
                "img": "http://orion-c.top/app"+imageUrl[0],
                "id": item[0],
                "title": item[1],
                "read_count": item[4],
                "add_time": item[3].strftime('%Y-%m-%d'),
            })
    sql = 'select * from fwpic_list ORDER by add_time DESC'
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) > 0:
        for item in queryList:
            atSql = 'select url from attachment where id in (%s)'%item[5]
            dbc.execute(atSql)
            imageUrl = dbc.fetchone()
            # print urlList
            # newUrlList = []
            # for image_item in urlList:
            #     newUrlList.append(image_item[0])
            fwpicList.append({
                "img": "http://orion-c.top/app"+imageUrl[0],
                "id": item[0],
                "title": item[1],
                "read_count": item[4],
                "add_time": item[3].strftime('%Y-%m-%d'),
            })
    result = {
        "gan": True,
        "gfpicList":gfpicList,
        "fwpicList": fwpicList,
    }
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getVoiceList', methods=['GET'])
def getVoiceList():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    voice_list = []
    voice_play_list = []

    sql = 'select * from voice_list ORDER by add_time DESC'
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) > 0:
        for item in queryList:
            atSql = 'select url from attachment where id in (%s)'%item[4]
            dbc.execute(atSql)
            imageUrl = dbc.fetchone()[0]
            atSql = 'select url from attachment where id in (%s)' % item[2]
            dbc.execute(atSql)
            voiceUrl = dbc.fetchone()[0]
            voice_list.append({
                "id": item[0],
                "title": item[1],
            })
            voice_play_list.append({
                "src":"http://orion-c.top/app"+voiceUrl,
                "poster":"http://orion-c.top/app"+imageUrl,
                "name":item[1],
                "author":"",
            })
    result = {
        "count":len(voice_list),
        "voice_list":voice_list,
        "voice_play_list": voice_play_list,
    }
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getPicDetail', methods=['GET'])
def getPicDetail():
    id = request.values.get("detailId")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')

    sql = 'select image_ids from pic_list where id = %s'
    dbc.execute(sql,(id,))
    imageIds = dbc.fetchone()[0]
    imageIds = imageIds.split(',')
    preview_list = []
    image_list = []
    for imageId in imageIds:
        atSql = 'select * from attachment where id in (%s)' % imageId
        dbc.execute(atSql)
        iamgeDetail = dbc.fetchone()
        imageId = iamgeDetail[0]
        imageUrl = iamgeDetail[2]
        preview_list.append("http://orion-c.top/app"+imageUrl)
        image_list.append({
                "img_url": "http://orion-c.top/app"+imageUrl,
                "id": imageId,
            })

    result = {
        "preview_list": preview_list,
        "image_list":image_list,

    }
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getPicFwDetail', methods=['GET'])
def getPicFwDetail():
    id = request.values.get("detailId")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'select * from fwpic_list where id = %s'
    dbc.execute(sql, (id,))
    detail = dbc.fetchone()
    page_list_sql = 'select * from fwdetail_list where pid = %s'
    dbc.execute(page_list_sql, (id,))
    page_list = dbc.fetchall()
    pageList = []
    for pageItem in page_list:
        if pageItem[2] == 'image':
            atSql = 'select url from attachment where id in (%s)' % pageItem[3]
            dbc.execute(atSql)
            imageUrl = dbc.fetchone()
            item_content = "http://orion-c.top/app"+imageUrl[0]
        else:
            item_content = pageItem[3]
        pageList.append({
            'content_type': pageItem[2],
            'content': item_content,
            'content_id': pageItem[0],
        })
    # 评论
    repaly_count_sql = 'select * from pinglun_list where ptype = "fwPic" and pid = %s and status = "1" ' % detail[0]
    dbc.execute(repaly_count_sql)
    repalyCountList = dbc.fetchall()
    replayList = []
    if len(repalyCountList) > 0:
        has_repaly = True
        for i in range(0, len(repalyCountList)):
            replayList.append({
                "id": repalyCountList[i][0],
                "avantar": repalyCountList[i][3],
                "user_name": repalyCountList[i][4],
                "replay_time": repalyCountList[i][6],
                "lou": len(repalyCountList) - i,
                "replay_desc": repalyCountList[i][5],
            })
    else:
        has_repaly = False
    result = {
        'title': detail[1],
        'fx_time': detail[3].strftime('%Y-%m-%d'),
        'fx_from': detail[2],
        'page_list': pageList,
        "has_replay_list": has_repaly,
        "replay_list":replayList,
    }
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/uploadTitleImage', methods=['POST'])
def uploadTitleImage():
    upload_file = request.files["videoImgae"]
    if upload_file:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')

        filename = secure_filename(upload_file.filename)
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
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '上传成功', 'content': {'attachment_id': attachment_id}})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '上传失败'})
        return response


@app.route('/uploadVideo', methods=['POST'])
def uploadVideo():
    upload_file = request.files["video"]
    if upload_file:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')

        filename = secure_filename(upload_file.filename)
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
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '上传成功', 'content': {'attachment_id': attachment_id}})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '上传失败'})
        return response


@app.route('/submitVideo', methods=['POST'])
def submitVideo():
    type = request.json.get("type")
    videoId = request.json.get("videoId")
    imageId = request.json.get("imageId")
    title = request.json.get("title")
    if type and videoId and imageId and title:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        # 入库
        sql = 'insert into video_list (title,image_id,video_id,video_type) VALUES (%s,%s,%s,%s)'
        dbc.execute(sql, (title, imageId, videoId, type))
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '添加成功'})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '添加失败'})
        return response


@app.route('/submitPic', methods=['POST'])
def submitPic():
    imageIds = request.json.get("imageIds")
    title = request.json.get("title")
    if imageIds and title:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        strImageIds = ",".join(imageIds)
        # 入库
        sql = 'insert into pic_list (title,image_ids) VALUES (%s,%s)'
        dbc.execute(sql, (title, strImageIds))
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '添加成功'})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '添加失败'})
        return response


@app.route('/getVideoListPC', methods=['GET'])
def getVideoListPC():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'select * from video_list ORDER by add_time DESC'
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) == 0:
        dbc.close()
        db.close()
        response = cors_response({"code": 10001, "msg": "还没有任务"})
        return response
    result = []
    for item in queryList:
        image_url_sql = 'select url from attachment where id = %s'
        dbc.execute(image_url_sql, (item[2],))
        image_url = dbc.fetchone()[0]

        video_url_sql = 'select url from attachment where id = %s'
        dbc.execute(video_url_sql, (item[3],))
        video_url = dbc.fetchone()[0]

        result.append({
            "id": item[0],
            "title": item[1],
            "image_url": image_url,
            "video_url": "http://orion-c.top/app"+video_url,
        })
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getPicListPC', methods=['GET'])
def getPicListPC():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'select * from pic_list ORDER by add_time DESC'
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) == 0:
        dbc.close()
        db.close()
        response = cors_response({"code": 10001, "msg": "还没有任务"})
        return response
    result = []
    for item in queryList:
        # atSql = 'select url from attachment where id in (%s)'%item[2]
        # print atSql
        # dbc.execute(atSql)
        # urlList = dbc.fetchall()
        # print urlList
        # newUrlList = []
        # for image_item in urlList:
        #     newUrlList.append(image_item[0])
        result.append({
            "id": item[0],
            "title": item[1],
        })
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/submitfwPic', methods=['POST'])
def submitfwPic():
    title = request.json.get("title")
    fromValue = request.json.get("from")
    imageId = request.json.get("imageId")
    if title:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        # 入库
        sql = 'insert into fwpic_list (title,from_value,image_id) VALUES (%s,%s,%s)'
        dbc.execute(sql, (title, fromValue,imageId))
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '添加成功'})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '添加失败'})
        return response


@app.route('/submitVoice', methods=['POST'])
def submitVoice():
    title = request.json.get("title")
    voiceId = request.json.get("voiceId")
    imageId = request.json.get("imageId")
    if title:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        # 入库
        sql = 'insert into voice_list (title,voice_id,image_id) VALUES (%s,%s,%s)'
        dbc.execute(sql, (title, voiceId,imageId))
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '添加成功'})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '添加失败'})
        return response


@app.route('/submitfwPicDetail', methods=['POST'])
def submitfwPicDetail():
    id = request.json.get("id")
    imageId = request.json.get("imageId")
    desc = request.json.get("desc")
    type = request.json.get("type")
    if type and id:
        # 连接
        db = MySQLdb.connect(database_host, database_username, database_password, database1)
        dbc = db.cursor()
        # 编码问题
        db.set_character_set('utf8')
        dbc.execute('SET NAMES utf8;')
        dbc.execute('SET CHARACTER SET utf8;')
        dbc.execute('SET character_set_connection=utf8;')
        # 入库
        if type == 'text':
            sql = 'insert into fwdetail_list (pid,content_type,content) VALUES (%s,%s,%s)'
            content = desc
        else:
            sql = 'insert into fwdetail_list (pid,content_type,content) VALUES (%s,%s,%s)'
            content = imageId
        dbc.execute(sql, (id, type, content))
        db.commit()
        dbc.close()
        db.close()
        response = cors_response({'code': 0, 'msg': '添加成功'})
        return response
    else:
        response = cors_response({'code': 10001, 'msg': '添加失败'})
        return response


@app.route('/getfwPicListPC', methods=['GET'])
def getfwPicListPC():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'select * from fwpic_list ORDER by add_time DESC'
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) == 0:
        dbc.close()
        db.close()
        response = cors_response({"code": 10001, "msg": "还没有任务"})
        return response
    result = []
    for item in queryList:
        atSql = 'select url from attachment where id = %s'%item[5]
        dbc.execute(atSql)
        url = dbc.fetchone()
        # print urlList
        # newUrlList = []
        # for image_item in urlList:
        #     newUrlList.append(image_item[0])
        result.append({
            "id": item[0],
            "title": item[1],
            "from_value": item[2],
            "image_url":url[0],
        })
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getVoiceListPC', methods=['GET'])
def getVoiceListPC():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'select * from voice_list ORDER by add_time DESC '
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) == 0:
        dbc.close()
        db.close()
        response = cors_response({"code": 10001, "msg": "还没有任务"})
        return response
    result = []
    for item in queryList:
        atSql = 'select url from attachment where id = %s'
        dbc.execute(atSql, (item[2],))
        url = dbc.fetchone()
        result.append({
            "id": item[0],
            "title": item[1],
            "voice_url": url[0],
        })
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getPingLunListPC', methods=['GET'])
def getPingLunListPC():
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'select * from pinglun_list ORDER by add_time DESC '
    dbc.execute(sql)
    queryList = dbc.fetchall()
    if len(queryList) == 0:
        dbc.close()
        db.close()
        response = cors_response({"code": 10001, "msg": "还没有任务"})
        return response
    result = []
    for item in queryList:
        if item[1] == 'voice':
            atSql = 'select title from voice_list where id = %s'
            dbc.execute(atSql, (item[2],))
            title = dbc.fetchone()
        if item[1] == 'vedio':
            atSql = 'select title from video_list where id = %s'
            dbc.execute(atSql, (item[2],))
            title = dbc.fetchone()
        if item[1] == 'gfPic':
            atSql = 'select title from pic_list where id = %s'
            dbc.execute(atSql, (item[2],))
            title = dbc.fetchone()
        if item[1] == 'fwPic':
            atSql = 'select title from fwpic_list where id = %s'
            dbc.execute(atSql, (item[2],))
            title = dbc.fetchone()
        try:
            result.append({
                "id": item[0],
                "title": title[0],
                "user_name": item[4],
                "pinglun_dec": item[5],
                "add_time": item[6].strftime('%Y-%m-%d'),
                "status": item[7],
            })
        except:
            continue
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response


@app.route('/getfwPicDetailPC', methods=['POST'])
def getfwPicDetailPC():
    id = request.json.get("id")
    # 连接
    db = MySQLdb.connect(database_host, database_username, database_password, database1)
    dbc = db.cursor()
    # 编码问题
    db.set_character_set('utf8')
    dbc.execute('SET NAMES utf8;')
    dbc.execute('SET CHARACTER SET utf8;')
    dbc.execute('SET character_set_connection=utf8;')
    sql = 'select * from fwpic_list WHERE id = %s'
    dbc.execute(sql, (id,))
    query = dbc.fetchone()
    if len(query) == 0:
        dbc.close()
        db.close()
        response = cors_response({"code": 10001, "msg": "还没有任务"})
        return response
    detailSql = 'select * from fwdetail_list WHERE pid = %s'
    dbc.execute(detailSql, (id,))
    detailList = dbc.fetchall()
    detailResult = []
    if len(detailList) > 0:
        for item in detailList:
            if item[2] == 'image':
                atSql = 'select url from attachment where id = %s'
                dbc.execute(atSql, (item[3],))
                url = dbc.fetchone()
                detail_content = url[0]
            else:
                detail_content = item[3]
            detailResult.append({
                "id": item[0],
                "content_type": item[2],
                "content": detail_content,
            })
    result = {
        "id": query[0],
        "title": query[1],
        "from_value": query[2],
        "detail_list": detailResult,
    }
    dbc.close()
    db.close()
    response = cors_response({'code': 0, 'msg': '', 'content': result})
    return response
