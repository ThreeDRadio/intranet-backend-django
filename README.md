# Three D Intranet

A Django application built on top of the legacy Three D music catalogue.

## Configuration

### Deleting Orphaned Comments

The legacy database used IDs for relations between tables, but did not use
foreign keys. This means that there are quite a few orphaned comments from
releases being removed from the catalogue without cleaning up the comments.

Database migrations will not work until these have been cleaned, which can be
done with the following SQL:

```sql
DELETE FROM cdcomment
WHERE id IN (
  SELECT cdcomment.id FROM cdcomment
  LEFT JOIN cd on cdcomment.cdid = cd.id
  WHERE cd.id IS NULL
)
```

### Migrating old users

We need to migrate users from the old `users` table into Django.

```bash
./manage.py shell < session/import_users.py
```
