from datetime import datetime

from application import db


class Subscription(db.Model):
    '''
        用户订阅模型
    '''
    __tablename__ = 'subscription'

    user = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.Integer, nullable=False)
    target_type = db.Column(db.String, nullable=False)
    action = db.Column(db.String, nullable=False)
    created = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return '<user %r>' % self.user


class Notify(db.Model):
    '''
        消息表模型
    '''
    __tablename__ = 'notify'

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer) #发送者的ID
    target = db.Column(db.Integer) #该条提醒所关联的对象
    target_type = db.Column(db.String(256)) #消息类型，文章，用户等
    type = db.Column(db.INTEGER, nullable=False) #[1公告Announce， 2提醒Remind， 3信息Message]
    content = db.Column(db.Text)  #消息的内容
    action = db.Column(db.String(256)) #提醒信息的动作类型，（喜欢，评论，关注等）
    created = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return '<sender %r>' % self.sender



class UserNotify(db.Model):
    '''
        用户消息队列模型
    '''
    __tablename__ = 'user_notify'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, nullable=False)
    notify = db.Column(db.Integer, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False)
    created = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return '<user %r>' % self.user


class User_friend_follow(db.Model):
    '''
        用户好友模型
    '''
    __tablename__ = 'user_friend_follow'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<user %r>' % self.user_id

class User_message(db.Model):
    '''
        用户动态模型
    '''
    __tablename__ = 'user_message'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return '<id %r>' % self.id

class System_message(db.Model):
    '''
        系统消息模型
    '''
    __tablename__ = 'system_message'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return '<id %r>' % self.id




