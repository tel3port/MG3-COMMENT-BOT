import uuid
import os

print(uuid.uuid4().hex)

def git_push():
    os.system('git add .')
    os.system('git commit -m "added more static urls"')
    os.system('git push https://tel3port:AjTdJsetif3Q5dn@github.com/tel3port/MG3-COMMENT-BOT.git --all')



git_push()