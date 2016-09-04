# coding:utf-8

from flask import current_app, request, url_for, abort
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from .exceptions import ValidationError
from random import randrange
import re


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xFF, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Like(db.Model):
    __tablename__ = 'likes'
    liker_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    liked_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    gender = db.Column(db.Integer, default=0)
    about_me = db.Column(db.String(128))
    self_intro = db.Column(db.String(512))
    job = db.Column(db.String(32))
    location = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    liked = db.relationship('Like',
                            foreign_keys=[Like.liker_id],
                            backref=db.backref('liker', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscribe', backref='subscriber', lazy='dynamic')
    usernotifies = db.relationship('UserNotify', backref='user', lazy='dynamic')
    sent_notifies = db.relationship('Notify', backref='sender', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['SEASIDE_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_password_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset_password': self.id})

    def reset_password(self, token, password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset_password') != self.id:
            return False
        self.password = password
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://cn.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            db.session.commit()
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            self.subscribe(user, TargetType.USER)
            n = User.create_remind(self, user, TargetType.USER, ActionType.FOLLOW)
            un = UserNotify(user=user, notify=n)
            db.session.add_all([f, n, un])
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            self.cancel_subscription(user, TargetType.USER)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def like(self, post):
        if not self.is_liking(post):
            l = Like(liker=self, liked=post)
            db.session.add(l)
            db.session.commit()

    def cancel_like(self, post):
        l = self.liked.filter_by(liked_id=post.id).first()
        if l:
            db.session.delete(l)

    def is_liking(self, post):
        return self.liked.filter_by(liked_id=post.id).first() is not None

    def subscribe(self, target, target_type):
        if not self.is_subscribing(target, target_type):
            s = Subscribe(subscriber=self, target_id=target.id, target_type=target_type)
            db.session.add(s)
            db.session.commit()

    def cancel_subscription(self, target, target_type):
        s = self.subscriptions.filter_by(target_id=target.id, target_type=target_type).first()
        if s:
            db.session.delete(s)

    def is_subscribing(self, target, target_type):
        return self.subscriptions.filter_by(target_id=target.id, target_type=target_type).first() is not None

    def send_message(self, receiver, body):
        n = Notify(
            body=body, type=NotifyType.MESSAGE, action=ActionType.SEND,
            target_id=receiver.id, target_type=TargetType.USER, sender=self)
        un = UserNotify(user=receiver, notify=n)
        db.session.add_all([n, un])
        db.session.commit()

    @staticmethod
    def create_remind(sender, target, target_type, action):
        notification = Notify(
            type=NotifyType.REMIND, target_id=target.id, target_type=target_type, action=action, sender=sender)
        return notification

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    @staticmethod
    def axl_follow_all():
        axl = User.query.filter_by(username='axl').first()
        for user in User.query.all():
            axl.follow(user)
            db.session.add(axl)
            db.session.commit()

    @staticmethod
    def axl_unfollow_all():
        axl = User.query.filter_by(username='axl').first()
        for user in User.query.all():
            axl.unfollow(user)
            db.session.add(axl)
            db.session.commit()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)  # update table 'follows'
                db.session.add(user)  # update table 'users'
                db.session.commit()

    @property
    def like_count(self):
        return db.session.query(Like).select_from(Post).filter_by(author_id=self.id).\
            join(Like, Post.id == Like.liked_id).count()

    @property
    def messages(self):
        return UserNotify.query.join(Notify, Notify.id == UserNotify.notify_id).\
            filter(UserNotify.user_id == self.id, Notify.type == NotifyType.MESSAGE)

    @property
    def reminds(self):
        return UserNotify.query.join(Notify, Notify.id == UserNotify.notify_id).\
            filter(UserNotify.user_id == self.id, Notify.type == NotifyType.REMIND).\
            join(User, )



    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        json_user = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
            'posts_count': self.posts.count(),
        }
        return json_user


class AnonymousUser(AnonymousUserMixin):

    confirmed = False

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80


taggings = db.Table('taggings',
                    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    liker = db.relationship('Like', foreign_keys=[Like.liked_id],
                            backref=db.backref('liked', lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=taggings, backref=db.backref('posts', lazy='dynamic'), lazy='dynamic')
    tag_string = db.Column(db.String(128))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count-1)).first()
            p = Post(title=forgery_py.lorem_ipsum.sentence(),
                     body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code', 'em', 'i', 'img', 'li', 'ol',
                        'p', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3']
        allowed_attributes = {
            'a': ['href', 'title'],
            'abbr': ['title'],
            'acronym': ['title'],
            'img': ['alt', 'src', 'style'],
            'code': ['class']
        }

        target.body_html = bleach.linkify(
            bleach.clean(
                markdown(value, output_format='html'), tags=allowed_tags, attributes=allowed_attributes, strip=True))

    def pretty_oneline(self):

        def sub_str_by_bytes(text, n):
            length = 0
            i = 0
            while i < len(text):
                if re.match(r'^[\x00-\xff]', text[i]):
                    length += 1
                else:
                    length += 2
                i += 1
                if length >= n:
                    break

            if i < len(text):
                return text[0: length] + ' ...'
            else:
                return text

        if self.body_html:
            one_line = self.body_html
        else:
            one_line = self.body

        return sub_str_by_bytes(re.sub(r'<[^>]+>|\s+', ' ', one_line), 82)

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count(),
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)

    @staticmethod
    def generate_filename():
        filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
        return '%s%s' % (filename_prefix, str(randrange(1000, 10000)))

    @staticmethod
    def on_changed_tag_string(target, value, oldvalue, initiator):
        tag_array = value.split(';')
        tags = []
        for t in tag_array:
            tag = Tag.query.filter_by(name=t).first()
            if tag is not None:
                tags.append(tag)

        target.tags = tags

db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Post.tag_string, 'set', Post.on_changed_tag_string)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        post_count = Post.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count-1)).first()
            p = Post.query.offset(randint(0, post_count-1)).first()
            c = Comment(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        timestamp=forgery_py.date.date(True), post=p, author=u)
            db.session.add(c)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code', 'em',  'li', 'ol',
                        'p', 'pre', 'strong', 'ul']
        allowed_attributes = {
            'a': ['href', 'title'],
            'abbr': ['title'],
            'acronym': ['title'],
            'code': ['class']
        }

        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'),
                         tags=allowed_tags, attributes=allowed_attributes, strip=True))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class TagTree(db.Model):
    __tablename__ = 'tagtrees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), index=True, unique=True)
    tags = db.relationship('Tag', backref='tagtree', lazy='dynamic')

    def __repr__(self):
        return "<TagTree: %r>" % self.name

    @staticmethod
    def insert_tagtrees():
        trees = ['前端框架', 'Javascript', '分词搜索', 'Web框架', '编程语言', '数据库', '云平台']
        for t in trees:
            tree = TagTree.query.filter_by(name=t).first()
            if tree is None:
                tree = TagTree(name=t)
                db.session.add(tree)
        db.session.commit()


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24), index=True, unique=True)
    intro = db.Column(db.String(128))
    tagtree_id = db.Column(db.Integer, db.ForeignKey('tagtrees.id'))

    def __repr__(self):
        return '<Tag: %r>' % self.name

    @staticmethod
    def insert_tags():
        mapper = {'前端框架': ["Bootstrap", "AngularJs", "React", "Boilerplate", 'Jinja'],
                  'Javascript': ["JavaScript", "JQuery", "JSON", "AJAX"],
                  '分词搜索': ["搜索引擎", "中文分词", "全文检索", "Whoosh", "jieba"],
                  'Web框架': ["Flask", "Tornado", "Django", "Web2Py"],
                  '编程语言': ["C++", "Python", "Java"],
                  '数据库': ["SQLite", "MySQL", "Redis", "Rabbitmq", "NoSQL"],
                  '云平台': ['Heroku', 'SAE', 'DigitalOcean']}
        for treename in mapper:
            tree = TagTree.query.filter_by(name=treename).first()
            for tagname in mapper[treename]:
                tag = Tag.query.filter_by(name=tagname).first()
                if tag is None:
                    tag = Tag(name=tagname, tagtree=tree)
                    db.session.add(tag)
            db.session.commit()


class Notify(db.Model):
    """The notification model.

    :class:`.Notify` is used to record 3 kinds of information:
        1. Announce; 2. Remind; 3. Message

    *All notifications could be described like: (`A`) (`do something` to|in`) (`B`)|(in `B's something`)
    `A` triggers off a notification, marked as :attr:`.sender`.
    `do something` to|in`, marked as :attr:`.action`, is the corresponding action of a notification
    could be one of `like`, `comment`, `post` & `follow`.
    `B` or `B's something` the :attr:`.target` of a notification.

    e.g.
    `Axl` `follow` `Slash`:
        sender = `Axl`; action = `follow`; target = `Slash` & target_type = `user`

    `Axl` `like` `Slash's post: Paradise City`
        sender = `Axl`; action = `like`; target = `Paradise City` $ target_type = `post`

    `Axl` `send message to` `Slash`
        sender = `Axl`; action = `send`; body = `message`; target = `Slash` & target_type = `user`
    """
    __tablename__ = 'notifies'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    type = db.Column(db.Integer, nullable=False)
    target_id = db.Column(db.Integer)
    target_type = db.Column(db.Integer)
    action = db.Column(db.Integer)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_notifies = db.relationship(
        'UserNotify', backref='notify', cascade='all, delete-orphan', lazy='dynamic')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Notify sender:%r, action:%r, target:%r>' % (self.sender_id, self.action, self.target_id)


class UserNotify(db.Model):
    __tablename__ = 'usernotifies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_read = db.Column(db.Boolean, default=False)
    notify_id = db.Column(db.Integer, db.ForeignKey('notifies.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<UserNotify user:%r, read:%r, notify:%r>' % (self.user_id, self.is_read, self.notify_id)


class Subscribe(db.Model):
    __tablename__ = 'subscribes'
    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer)
    target_type = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Subscribe user:%r, target:%r %r>' % (
            self.user_id, 'USER' if self.target_type == TargetType.USER else 'POST', self.target_id,)


class NotifyType(object):
    ANNOUNCE = 0x01
    REMIND = 0x02
    MESSAGE = 0x03


class ActionType(object):
    LIKE = 0x01
    FOLLOW = 0x02
    POST = 0x03
    COMMENT = 0x04
    SEND = 0x05


class TargetType(object):
    USER = 0x01
    POST = 0x02
