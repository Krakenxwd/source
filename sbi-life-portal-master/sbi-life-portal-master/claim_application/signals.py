from django.db.models.signals import post_save
from django.dispatch import receiver

from claim_application.constant import CODE_CHOICE
from claim_application.models import ValidationConfiguration, ValidationRuleEngine


@receiver(post_save, sender=ValidationConfiguration)
def add_validation_rule_validation_configuration_created(sender, instance, created, **kwargs):
    if created:
        for code in CODE_CHOICE:
            ValidationRuleEngine.objects.create(validation_configuration=instance,
                                           validation_code=code[0],
                                           validation_action=ValidationRuleEngine.OFF,
                                           validation_description=code[1])
    else:
        for code in CODE_CHOICE:
            if not ValidationRuleEngine.objects.filter(validation_configuration=instance, validation_code=code[0],
                                                  validation_description=code[1]).exists():
                ValidationRuleEngine.objects.create(validation_configuration=instance, validation_code=code[0],
                                               validation_action=ValidationRuleEngine.OFF,
                                               validation_description=code[1])
        print("Completed Adding validation")
