"""Test Instagram data collection"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from collectors.instagram_api import InstagramAPI

api = InstagramAPI()
posts, pks = api.get_comprehensive_post_data('Samsung TV', 3)
print(f'Posts: {len(posts)}, PKs: {pks}')

comments = api.get_comprehensive_comments(pks, 20)
print(f'\nTotal comments: {len(comments)}')
for i, c in enumerate(comments[:5], 1):
    text = c["comment_text"][:60].encode('ascii', 'ignore').decode('ascii')
    print(f'{i}. @{c["author_username"]}: {text}...')

print(f'\nSample post data:')
print(f'  Author: {posts[0]["author_username"]}')
print(f'  Caption: {posts[0]["caption"][:80].encode("ascii", "ignore").decode("ascii")}...')
print(f'  Likes: {posts[0]["like_count"]}, Comments: {posts[0]["comment_count"]}')
