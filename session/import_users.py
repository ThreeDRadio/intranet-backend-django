

def createEditorsGroup():
    from django.contrib.auth.models import Group
    if not Group.objects.filter(name="Catalogue Editors").exists():
        print("Editors group not found, creating")
        return Group.objects.create(name="Catalogue Editors")
    else:
        print("Using existing editors group")
        return Group.objects.get(name="Catalogue Editors")

def importUsers(editors):
    from session.models import OldUser, OldPassword
    from django.contrib.auth.models import User
    all_users = OldUser.objects.all()
    for u in all_users:
        if User.objects.filter(username=u.username).exists():
            newUser = User.objects.get(username=u.username)
        else:
            newUser = User.objects.create_user(u.username)
        if u.first is not None:
            newUser.first_name = u.first
        if u.last is not None:
            newUser.last_name = u.last
        if u.admin == True:
            newUser.is_staff = True
        if u.cdeditor == True:
            editors.user_set.add(newUser)
        if u.active == True:
            newUser.is_active = True
        else:
            newUser.is_active = False
        if u.password is not None:
            OldPassword.objects.filter(user=newUser).delete()
            OldPassword.objects.create(user=newUser, password=u.password)
        newUser.save()
    

editors = createEditorsGroup()
importUsers(editors)
