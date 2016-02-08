# -*- coding: utf-8 -*-
from . import r,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import UserMixin
from main.MU_update import BreakInQueue,DeletePage,GetImage
from main.MU_conf import MU_MainConfig
import time
import datetime
import os
import sys
reload(sys)
import pdb
sys.setdefaultencoding('utf8')
class User(UserMixin,object):
    def AddUser(self,username,password,role,email):
        self.password=password
        r.lpush('users',username)
        r.hset('pwd',username,self.password_hash)
        r.hset('role',username,role)
        r.hset('email',username,email)
    def RemUser(self,username):
        r.hdel('pwd',username)
        r.hdel('role',username)
        r.hdel('email',username)
    def ChangeRole(self,username,role):
        r.hset('role',username,role)
        return username
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)
    def GetPassword(self,username):
        self.password_hash=r.hget('pwd',username)
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
class Page(object):
    def GetTitles(self):
        pushinglist=r.zrange('queuenumber',0,-1)
        return pushinglist
    def Break(self,title):
        flag=BreakInQueue(title)
        return flag
    def Delete(self,title):
        flag=DeletePage(title)
        return flag          
    def Add(self,title):
        flag=GetImage(title.encode('utf8'))
        if flag==True:
            timenow=time.time()
            r.zadd('expire',MU_MainConfig.EDITEDPREFIX+title,timenow)
            r.hset('queue',MU_MainConfig.EDITEDPREFIX+title,title)
            r.zadd('queuenumber',title,0)
            scorequeue=r.zrange('queuenumber',0,-1)
            for i in range(len(scorequeue)):
                score=r.zscore('queuenumber',scorequeue[i])
                r.zadd('queuenumber',scorequeue[i],score+1)
            img=r.hget('img',MU_MainConfig.EDITEDPREFIX+title)
            r.hset('imgkey',title,img)
            return True
        else:
            return False