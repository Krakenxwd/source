from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def assign_group_when_user_created(sender, instance, created, **kwargs):
    if created:
        user_obj = instance
        member_g, member_g_created = Group.objects.get_or_create(name='member')
        user_obj.groups.add(member_g)