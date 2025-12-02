from app import db, User

for u in User.query.all():
    print(u.id, u.name, u.email)
