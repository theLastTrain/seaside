
# coding:utf-8


from flask import render_template, abort, flash, redirect, url_for, \
    request, current_app, make_response, g, jsonify
from flask.ext.login import login_required, current_user
from ..decorators import admin_required, permission_required, confirmation_required
from . import main
from .forms import EditProfileForm, PostForm, CommentForm, ChangeLogForm
from .. import db
from ..models import Permission, User, Role, Post, Comment, Changelog, Like
from flask.ext.sqlalchemy import get_debug_queries
import os
from time import sleep

# added May 17th 1:33 am, this block solves the problem:
#   UnicodeDecodeError: 'ascii' codec can't decode byte 0xe9 in position 0: ordinal not in range(128)
if 'heroku' == os.environ.get('FLASK_COVERAGE'):
    import sys
    if sys.getdefaultencoding() != 'utf8':
        reload(sys)
        sys.setdefaultencoding('utf8')
        default_encoding = sys.getdefaultencoding()
from .forms import SearchForm


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['SEASIDE_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    changelogs = Changelog.query.order_by(Changelog.timestamp.desc())[0:9]
    return render_template('index.html',
                           pagination=pagination, posts=posts, changelogs=changelogs, show_followed=show_followed)


@main.route('/all')
@login_required
@confirmation_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
@confirmation_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "Administrator only!"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderator():
    return "For comment moderators!"


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    like_cnt = Like.query.filter(Like.liked.has(Post.author == user)).count()
    posts = user.posts.order_by(Post.timestamp.desc())[0:3]
    return render_template('user.html', user=user, posts=posts, like_cnt=like_cnt)


@main.route('/user/<username>/posts')
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    cnt = user.posts.count()
    pagination = None
    if cnt <= current_app.config['SEASIDE_POSTS_PER_CARD']:
        posts = user.posts.order_by(Post.timestamp.desc()).all()
    else:
        pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['SEASIDE_POSTS_PER_CARD'],
            error_out=False)
        posts = pagination.items
    return render_template('_user_posts.html', section_title='全部文章',
                           user=user, posts=posts, pagination=pagination, endpoint='.user_posts')


@main.route('/user/<username>/likes')
@login_required
def liked_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    cnt = user.liked.count()
    pagination = None
    if cnt <= current_app.config['SEASIDE_POSTS_PER_CARD']:
        posts = [item.liked for item in user.liked.order_by(Like.timestamp.desc())]
    else:
        pagination = user.liked.order_by(Like.timestamp.desc()).paginate(
            page, per_page=current_app.config['SEASIDE_POSTS_PER_CARD'],
            error_out=False)
        posts = [item.liked for item in pagination.items]
    return render_template('_user_posts.html', section_title='喜欢的文章',
                           user=user, posts=posts, pagination=pagination, endpoint='.liked_posts')


@main.route('/followers/<username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    cnt = user.followers.count()
    pagination = None
    if cnt <= current_app.config['SEASIDE_FOLLOWERS_PER_PAGE'] + 1:
        follows = [item.follower for item in user.followers][1:]
    else:
        pagination = user.followers.paginate(
            page, per_page=current_app.config['SEASIDE_FOLLOWERS_PER_PAGE'],
            error_out=False)
        follows = [item.follower for item in pagination.items]
    section_title = '被 <strong>' + str(cnt - 1) + '</strong> 人关注'
    return render_template('_user_followers.html', user=user, section_title=section_title,
                           endpoint='.followers', pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')
@login_required
def followed_by(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    cnt = user.followed.count()
    pagination = None
    if cnt <= current_app.config['SEASIDE_FOLLOWERS_PER_PAGE'] + 1:
        follows = [item.follower for item in user.followed][1:]
    else:
        pagination = user.followed.paginate(
            page, per_page=current_app.config['SEASIDE_FOLLOWERS_PER_PAGE'],
            error_out=False)
        follows = [item.followed for item in pagination.items]
    section_title = '关注了 <strong>' + str(user.followed.count() - 1) + '</strong> 人'
    return render_template('_user_followers.html', user=user, section_title=section_title,
                           endpoint='.followed_by', pagination=pagination, follows=follows)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.gender = form.gender.data
        current_user.about_me = form.about_me.data
        current_user.self_intro = form.self_intro.data
        current_user.job = form.job.data
        current_user.location = form.location.data
        db.session.add(current_user)
        db.session.commit()
        # flash('用户资料已更新', category='success')
        return redirect(url_for('.user', username=current_user.username))
    form.gender.data = current_user.gender
    form.about_me.data = current_user.about_me
    form.self_intro.data = current_user.self_intro
    form.job.data = current_user.job
    form.location.data = current_user.location
    # return render_template('edit_profile.html', form=form)
    return render_template('edit_profile.html', form=form, user=current_user)


# @main.route('/edit-profile/location', methods=['POST'])
# @confirmation_required
# @login_required
# def edit_location():
#     if request.method == 'POST':
#         location = request.form.get('location', 'fuck')
#         current_user.location = location
#         db.session.add(current_user)
#         db.session.commit()
#         return location


# @main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def edit_profile_admin(id):
#     user = User.query.get_or_404(id)
#     form = EditProfileAdminForm(user=user)
#     if form.validate_on_submit():
#         user.email = form.email.data
#         user.username = form.username.data
#         user.confirmed = form.confirmed.data
#         user.role = Role.query.get(form.role.data)
#         user.name = form.name.data
#         user.location = form.location.data
#         user.about_me = form.about_me.data
#         db.session.add(user)
#         db.session.commit()
#         flash('用户资料已更新')
#         return redirect(url_for('.user', username=user.username))
#     form.email.data = user.email
#     form.username.data = user.username
#     form.confirmed.data = user.confirmed
#     form.role.data = user.role_id
#     form.name.data = user.name
#     form.location.data = user.location
#     form.about_me.data = user.about_me
#     return render_template('edit_profile.html', form=form)


@main.route('/write-post', methods=['GET', 'POST'])
@login_required
@confirmation_required
def write_post():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('write_post.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
@confirmation_required
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('评论已提交', category='success')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
            current_app.config['SEASIDE_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['SEASIDE_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('文章已更新', category='success')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('write_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@confirmation_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在', category='danger')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        current_user.unfollow(user)
        return jsonify({'following': False})
    else:
        current_user.follow(user)
        return jsonify({'following': True})


@main.route('/like/<int:id>')
@login_required
@confirmation_required
@permission_required(Permission.FOLLOW)
def like(id):
    post = Post.query.get_or_404(id)
    if post is None:
        flash('文章不存在呢', category='danger')
        return redirect(url_for('.index'))
    if current_user.is_liking(post):
        current_user.cancel_like(post)
        cnt = post.liker.count()
        return jsonify({
                    'liking': False,
                    'cnt': cnt,
        })
    else:
        current_user.like(post)
        cnt = post.liker.count()
        return jsonify({
                    'liking': True,
                    'cnt': cnt,
        })


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['SEASIDE_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration, query.context))
    return response


# @main.before_app_request
# def before_request():
#     g.search_form = SearchForm()
#     g.changelog_form = ChangeLogForm()
    # g.post_form = PostForm()


# @main.route('/search', methods=['POST'])
# @login_required
# def search():
#     if not g.search_form.validate_on_submit():
#         return redirect(url_for('.index'))
#     return redirect(url_for('.search_results', query=g.search_form.search.data))


@main.route('/search-results/<query>')
@login_required
def search_results(query):
    posts = Post.query.whoosh_search(query, current_app.config['MAX_SEARCH_RESULTS']).all()
    return render_template('search_results.html', query=query, posts=posts)


# @main.route('/changelog', methods=['POST'])
# # @permission_required(Permission.ADMINISTER)
# def changelog():
#     if g.changelog_form.validate_on_submit():
#         chglog = Changelog(body=g.changelog_form.body.data)
#         db.session.add(chglog)
#         db.session.commit()
#         flash('更新日志已提交')
#         return redirect(url_for('.index'))


@main.route('/ckupload/', methods=['POST'])
def ckupload():

    """ckeditor file upload"""

    error = ''
    url = ''
    callback = request.args.get('CKEditorFuncNum')

    if request.method == 'POST' and 'upload' in request.files:
        file_obj = request.files['upload']
        file_name, file_ext = os.path.splitext(file_obj.filename)
        rd_name = '%s%s' % (Post.generate_filename(), file_ext)

        file_path = os.path.join('./app/static', 'upload', rd_name)

        dirname = os.path.dirname(file_path)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except :
                error = 'ERROR_CREATE_UPLOAD_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_ACCESSIBLE'
        if not error:
            file_obj.save(file_path)
            url = url_for('static', filename='%s/%s' % ('upload', rd_name))
    else:
        error = '405 Method not allowed'
    # JSONP, main./ckupload/?callback=CKEditorFuncNum
    res = '''
    <script typt="text/javascript">
        window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
    </script>''' % (callback, url, error)
    response = make_response(res)
    response.headers['Content-Type'] = 'text/html'
    return response


@main.route('/long-polling')
def long_polling():
    i = 0
    while True:
        if i == 10:
            return jsonify({'error': 0})
        else:
            i += 1
            sleep(5)
