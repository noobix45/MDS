# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q,Manager
from django.db.models.functions import Now
from django.contrib.auth.models import User
from django.utils import timezone


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Grup(models.Model):
    id_grup = models.AutoField(primary_key=True)
    nume_grup = models.CharField(max_length=20)
    lider = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'grup'


class Task(models.Model):
    id_task = models.AutoField(primary_key=True)
    titlu = models.CharField(max_length=50, blank=True, null=True)
    importanta = models.SmallIntegerField()
    deadline = models.DateField(blank=True, null=True)
    grup_task = models.BooleanField(blank=True, null=True,default=False)
    repetitiv = models.BooleanField(blank=True, null=True,default=False)
    days_to_do = ArrayField(models.SmallIntegerField(), blank=True, null=True)
    def_time = models.TimeField(blank=True, null=True)
    data_creare = models.DateTimeField(blank=True, null=True,default=timezone.now)
    data_completare = models.DateField(blank=True, null=True)
    prioritate = models.FloatField(null=True,blank=True,default=0.0)
    objects = models.Manager()

    def __str__(self):
        return self.titlu or f"Task #{self.id_task}"

    class Meta:
        managed = False
        db_table = 'task'
        constraints = [
            models.CheckConstraint(check=models.Q(deadline__gte=Now()), name='valid_date'),
            models.CheckConstraint(check=models.Q(importanta__gte=1, importanta__lte=5), name='importanta_v'),
        ]


class Notificare(models.Model):
    id_notificare = models.AutoField(primary_key=True)
    id_task = models.ForeignKey('Task', models.CASCADE, db_column='id_task')
    notif_dt = models.DateTimeField()
    mesaj = models.CharField(max_length=50, blank=True, null=True)
    trimis = models.BooleanField(blank=True,null=True,default=False)

    class Meta:
        managed = False
        db_table = 'notificare'
        constraints = [
            models.CheckConstraint(check=Q(notif_dt__gt=Now()), name='valid_time1')
        ]


class Utilizator(models.Model):
    id_utilizator = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE,db_column='id_user')
    objects: Manager["Utilizator"] = models.Manager()

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        managed = False
        db_table = 'utilizator'


class UtilizatorGrup(models.Model):
    # pk = models.CompositePrimaryKey('id_utilizator', 'id_grup')
    id_utilizator = models.ForeignKey(Utilizator, models.CASCADE, db_column='id_utilizator')
    id_grup = models.ForeignKey(Grup, models.CASCADE, db_column='id_grup')

    class Meta:
        managed = False
        db_table = 'utilizator_grup'
        unique_together = (('id_utilizator', 'id_grup'),)


class UtilizatorTask(models.Model):
    id = models.AutoField(primary_key=True)
    id_utilizator = models.ForeignKey(Utilizator, models.CASCADE, db_column='id_utilizator',related_name='taskuri_user')
    id_task = models.ForeignKey(Task, models.CASCADE, db_column='id_task',related_name='utilizatori_task')
    # objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'utilizator_task'
        unique_together = (('id_utilizator', 'id_task'),)
