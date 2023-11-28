"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
from models import db, connect_db, User, Post, Tag


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret'
app.app_context().push()


connect_db(app)
db.create_all()


@app.route("/")
def startup_page():
    """Redirect to list of Users."""

    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("posts/homepage.html", posts=posts)


@app.route("/users")
def show_all_users():
    """Show all users including links to more details"""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)


@app.route("/users/new")
def show_form():
    """Show add form for new users"""
    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def submit_form():
    """Process the add form, adding a newuser and going back to '/users' """
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()
    flash(f"User {new_user.full_name} added.")

    return redirect("/users")


@app.route("/users/<int:user_id>")
def show_info(user_id):
    """Show information about the given user"""
    user = User.query.get_or_404(user_id)
    return render_template('users/user_detail.html', user=user)


@app.route("/users/<int:user_id>/edit")
def show_edit_form(user_id):
    """Show the edit page for a user including a cancel button"""
    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def submit_edit_form(user_id):
    """Process the edit form, returning user to '/users' """
    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Delete the user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


@app.route("/users/<int:user_id>/posts/new")
def new_post(user_id):
    """ Show form to add a post for that user. """
    user = User.query.get_or_404(user_id)
    return render_template('posts/new.html', user=user)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def new_post_add(user_id):
    """Handle add form; add post and redirect to the user detail page."""
    user = User.query.get_or_404(user_id)
    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user)

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title}' added.")

    return redirect(f"/users/{user_id}")


@app.route("/posts/<int:post_id>")
def show_post(post_id):
    """Show a post. Show buttons to edit and delete the post."""
    post = Post.query.get_or_404(post_id)
    return render_template('posts/show.html', post=post)


@app.route("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """Show form to edit a post, and to cancel (back to user page)."""

    post = Post.query.get_or_404(post_id)
    return render_template('posts/edit.html', post=post)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post_commit(post_id):
    """Handle editing of a post. Redirect back to the post view."""
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    db.session.add(post)
    db.session.commit()
    flash(f"Post '{post.title}' edited.")

    return redirect(f"/users/{post.user_id}")


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    """Delete the post."""
    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title} deleted.")

    return redirect(f"/users/{post.user_id}")


@app.route("/tags")
def tags_index():
    """ Lists all tags, with links to the tag detail page."""

    tags = Tag.query.all()
    return render_template("tags/index.html", tags=tags)


@app.route("/tags/<int:tag_id>")
def tag_detail(tag_id):
    """Show detail about a tag. Have links to edit form and to delete."""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)


@app.route("/tags/new")
def new_tag():
    """Show detail about a tag. Have links to edit form and to delete."""
    posts = Post.query.all()
    return render_template('tags/new.html', posts=posts)


@app.route("/tags/new", methods=["POST"])
def new_tag_submit():
    """Process add form, adds tag, and redirect to tag list."""
    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)

    db.session.add(new_tag)
    db.session.commit()
    flash(f"Tag '{new_tag.name}' added.")

    return redirect("/tags")


@app.route("/tags/<int:tag_id>/edit")
def edit_tag(tag_id):
    """Show edit form for a tag."""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)


@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def edit_tag_submit(tag_id):
    """Process edit form, edit tag, and redirects to the tags list."""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' edited.")

    return redirect("/tags")


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    """Delete a tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.")

    return redirect("/tags")
