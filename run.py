import spider
import sys
import os
import json


'''
requires spider.py be in the same directory as this module
spider.py can be found at http://github.com/shariq/notion-on-firebase
'''


def get_firebase_json_path(firebase_path):
    return os.path.abspath(os.path.join(firebase_path, 'firebase.json'))


def add_to_firebase_json(firebase_path, new_rewrites):
    firebase_json_path = get_firebase_json_path(firebase_path)
    with open(firebase_json_path) as handle:
        firebase_json = json.loads(handle.read())
    if 'rewrites' not in firebase_json['hosting']:
        firebase_json['hosting']['rewrites'] = []
    existing_rewrites = firebase_json['hosting']['rewrites']
    for new_rewrite in new_rewrites:
        for existing_rewrite in existing_rewrites[:]:
            if existing_rewrite['destination'] == new_rewrite['destination']:
                print 'warning: removing', existing_rewrite
                existing_rewrites.remove(existing_rewrite)
            elif existing_rewrite['source'] == new_rewrite['source']:
                print 'warning: removing', existing_rewrite
                existing_rewrites.remove(existing_rewrite)
        existing_rewrites.append(new_rewrite)
    firebase_json['hosting']['rewrites'] = existing_rewrites
    dumped = json.dumps(firebase_json, indent=4)
    with open(firebase_json_path, 'w') as handle:
        handle.write(dumped)


def get_firebase_public_path(firebase_path):
    firebase_json_path = get_firebase_json_path(firebase_path)
    with open(firebase_json_path) as handle:
        contents = handle.read()
    relative_public = json.loads(contents)['hosting']['public']
    return os.path.join(firebase_path, relative_public)


def main(root_page, firebase_path):
    print 'root_page:', root_page
    print 'firebase_path:', firebase_path
    firebase_public_path = get_firebase_public_path(firebase_path)
    print 'firebase_public_path:', firebase_public_path
    print 'beginning spider...'
    rewrites = spider.run(root_page, firebase_public_path)
    print 'completed spider'
    print 'rewrites:', rewrites
    add_to_firebase_json(firebase_path, rewrites)
    original_path = os.getcwd()
    os.chdir(firebase_path)
    print 'deploying...'
    os.system('firebase deploy')
    os.chdir(original_path)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'usage: python run.py <root_notion_page_id> <firebase_path>'
        print 'e.g, python run.py d065149ff38a4e7a9b908aeb262b0f4f ../firebase'
        sys.exit(-1)
    firebase_path = sys.argv[-1]
    if not os.path.exists(firebase_path):
        print 'error: that firebase_path could not be found. '
        print '(path evaluated to {})'.format(os.path.abspath(firebase_path))
        sys.exit(-1)
    firebase_public_path = get_firebase_public_path(firebase_path)
    if not os.path.exists(os.path.join(firebase_public_path, 'ga.js')):
        print 'warning: ga.js was not found in your firebase public path'
        print 'hit enter after placing it there or if you don\'t want ga.js'
        print '(hint: this is a JS file from Google Analytics)'
        raw_input()
    root_page = sys.argv[-2]
    main(root_page, firebase_path)
