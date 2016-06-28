def importUsers():
    all_users = importer.models.User.objects.all()
    for u in all_users:
        print (u.username)
        newUser = User.objects.create_user(u.username)
        if u.first is not None:
            newUser.first_name = u.first
            newUser.save()
        if u.last is not None:
            newUser.last_name = u.last
            newUser.save()

