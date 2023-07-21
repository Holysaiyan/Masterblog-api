"""
This module contains the utility functions for managing blog posts
"""


from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def generate_id():
    """
    Generate a new unique ID for a post.
    """
    generated_id = max([key['id'] for key in POSTS]) + 1
    return generated_id


def find_post_by_id(post_id):
    """
    Find a post in the POSTS list by its ID.

    Args:
        post_id (int): The ID of the post to find.

    Returns:
        dict or None: The post dictionary if found, otherwise None.
    """
    for post in POSTS:
        if post['id'] == post_id:
            return post
    return None


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Get all the posts or sort the posts based on query parameters.

    Query Parameters:
        sort (str, optional): The field by which to sort posts. 'title' or 'content'.
        direction (str, optional): The sort direction. 'asc' or 'desc'.

    Returns:
        list: A list of post dictionaries.
    """
    sort_field = request.args.get('sort')
    direction = request.args.get('direction')

    # Validate the sort_field and direction parameters
    if sort_field and sort_field not in ['title', 'content']:
        error_message = {'error': 'Invalid sort field. Use "title" or "content".'}
        return jsonify(error_message), 400

    if direction and direction not in ['asc', 'desc']:
        error_message = {'error': 'Invalid direction. Use "asc" or "desc".'}
        return jsonify(error_message), 400

    # Perform sorting based on provided parameters
    if sort_field:
        if direction == 'asc':
            sorted_posts = sorted(POSTS, key=lambda post:
            post.get(sort_field, '').lower())
        else:  # direction == 'desc'
            sorted_posts = sorted(POSTS, key=lambda post:
            post.get(sort_field, '').lower(), reverse=True)
    else:
        sorted_posts = POSTS

    return jsonify(sorted_posts)


@app.route('/api/posts', methods=['POST'])
def add_posts():
    """
    Add a new post to the list of posts.

    Request Body:
        JSON object: {
            "title": "<title of the new post>",
            "content": "<content of the new post>"
        }

    Returns:
        dict: The newly added post dictionary.
    """
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        error_message = {'error': 'Both title and content are required.'}
        return jsonify(error_message), 400

    new_id = generate_id()
    new_post = {"id": new_id, "title": title, "content": content}
    POSTS.append(new_post)

    response = jsonify(new_post)
    response.status_code = 201
    return response


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a post by its ID.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        dict: A success message.
    """
    post = find_post_by_id(post_id)

    if post is None:
        error_message = {'error': 'Post not found'}
        return jsonify(error_message), 404

    POSTS.remove(post)
    success_message = {'message': f"Post with id {post_id} has been successfully deleted"}
    return jsonify(success_message), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update a post by its ID.

    Args:
        post_id (int): The ID of the post to update.

    Request Body:
        JSON object: {
            "title": "<updated title>",
            "content": "<updated content>"
        }

    Returns:
        dict: The updated post dictionary.
    """
    post = find_post_by_id(post_id)

    if not post:
        error_message = {'error': 'Post not found'}
        return jsonify(error_message), 404

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title and not content:
        error_message = {'error': 'Title or content is required for update.'}
        return jsonify(error_message), 400

    if title:
        post['title'] = title

    if content:
        post['content'] = content

    return jsonify(post), 200


@app.route('/api/posts/search')
def search():
    """
    Search for posts by title or content.

    Query Parameters:
        title (str, optional): Search posts by title.
        content (str, optional): Search posts by content.

    Returns:
        list or dict: A list of matching post titles or contents, or a message if no matches found.
    """
    title = request.args.get('title')
    content = request.args.get('content')

    if title:
        filtered_titles = [post['title'] for post in POSTS if title == post.get('title')]
        return jsonify(filtered_titles)
    elif content:
        filtered_contents = [post['content'] for post in POSTS if content.lower() in post.get('content', '').lower()]
        return jsonify(filtered_contents)
    else:
        available_titles = [post['title'] for post in POSTS]
        available_contents = [post['content'] for post in POSTS]
        return jsonify({
            "message": "Could not find any matching posts.",
            "available_titles": available_titles,
            "available_contents": available_contents
        })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
