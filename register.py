#!/usr/bin/env python
# -*- coding: utf-8 -*-

'A test module'
__author__ = 'FJY'

import os
import sys
import json, requests

gl_host = ''
gl_api_id = ''
gl_api_secret = ''
gl_group_id = ''
gl_person_id = ''
gl_history_dir = []

# 注册流程处理
def register_handle(params):
    global gl_person_id
    # 检测
    detect_resp = detection(params['file_url'])
    if detect_resp['status'] != 'ok':
        print 'detect_resp: '
        print detect_resp
    else:
        face_id = detect_resp['faces'][0]['face_id']
        if gl_person_id == '':
            # 创建person
            pc_resp = person_create(face_id, params['person_name'], params['person_phone'])
            if pc_resp['status'] == 'ok':
                gl_person_id = pc_resp['person_id']
                # 添加人到库
                group_add_person()
            else:
                print 'pc_resp: '
                print pc_resp
        else:
            # 添加人脸给人
            person_add_face()

# 人脸检测
def detection(file_url):
    http_url = gl_host + '/faces/detection'
    data = { 'api_id': gl_api_id, 'api_secret': gl_api_secret }
    headers = { 'Accept': 'application/json' }
    files = { 'file': ('test.jpg', open(file_url, 'rb'), 'image/jpeg') }
    resp = requests.post(http_url, data = data, files = files, headers=headers)
    return resp.json()

# 人脸库创建
def group_create(group_name):
    http_url = gl_host + '/groups/create'
    data = { 'api_id': gl_api_id, 'api_secret': gl_api_secret, 'name': group_name }
    headers = { 'Accept': 'application/json' }
    resp = requests.post(http_url, data = data, headers=headers)
    return resp.json()

# person创建
def person_create(face_id, name, phone):
    http_url = gl_host + '/people/create'
    data = { 'api_id': gl_api_id, 'api_secret': gl_api_secret, 'face_id': face_id, 'name': name, 'phone': phone }
    headers = { 'Accept': 'application/json' }
    resp = requests.post(http_url, data = data, headers=headers)
    return resp.json()

# 添加人到库
def group_add_person():
    http_url = gl_host + '/groups/add_person'
    data = { 'api_id': gl_api_id, 'api_secret': gl_api_secret, 'person_id': gl_person_id, 'group_id': gl_group_id }
    headers = { 'Accept': 'application/json' }
    resp = requests.post(http_url, data = data, headers=headers)
    return resp.json()

# 添加人脸到人
def person_add_face(face_id):
    http_url = gl_host + '/people/add_face'
    data = { 'api_id': gl_api_id, 'api_secret': gl_api_secret, 'person_id': gl_person_id, 'face_id': face_id }
    headers = { 'Accept': 'application/json' }
    resp = requests.post(http_url, data = data, headers=headers)
    return resp.json()
    

# 处理传入的参数
def handle_argv():
    global gl_host
    global gl_group_id
    global gl_history_dir
    args = sys.argv
    gl_host = args[1]
    # 注册文件信息
    top_dir = args[2] # 最外层文件夹
    group_name = args[3] # 库名
    group_id = args[4] # 库uuid
    # 读取历史数据信息
    file_object = open(top_dir + '/history.log', 'r')
    lines = file_object.readlines()
    for line in lines:
        gl_history_dir.append(line.strip())
    file_object.close()
    # 获取权限
    get_authorized()
    if group_id == '':
        # 创建一个库
        gc_resp = group_create(group_name)
        if gc_resp['status'] == 'ok':
            gl_group_id = gc_resp['group_id']
        else:
            print 'gc_resp: '
            print gc_resp
    else:
        gl_group_id = group_id
    # 开始注册
    walk_dir(top_dir)


# 遍历目标文件夹
def walk_dir(top_dir, topdown = True):
    global gl_person_id
    for root, dirs, files in os.walk(top_dir, topdown):
        for name in dirs:
            bottom_dir = os.path.join(root, name)
            判断是否读过
            if bottom_dir in gl_history_dir:
                print bottom_dir + '已存在'
            else:
                (person_name, person_phone) = name.split('-')
                person_id = ''
                for root, dirs, files in os.walk(bottom_dir, topdown):
                    for name in files:
                        file_url = os.path.join(root, name)
                        register_handle({
                            'file_url': file_url,
                            'person_name': person_name,
                            'person_phone': person_phone
                        })
                        print '跑到' + file_url
                        file_object = open(top_dir + '/history.log', 'a')
                        file_object.write(bottom_dir + '\n')
                        file_object.close()

    
# 获取权限
def get_authorized():
    global gl_api_id
    global gl_api_secret
    http_url = gl_host + '/get_authorized'
    resp = requests.get(url=http_url)
    data = resp.json()
    gl_api_id = data['api_id']
    gl_api_secret = data['api_secret']


# 初始化方法
def init():
    handle_argv()

# main
if __name__ == '__main__':
    init()
