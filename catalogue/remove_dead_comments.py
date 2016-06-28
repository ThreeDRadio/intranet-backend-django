from catalogue.models import Comment, Release

for comment in Comment.objects.all():
    if Release.objects.filter(id=comment.cdid).exists():
        pass
    else:
        print comment.cdid
        comment.delete()

print "Done!"
