from django.apps import apps
from django.core.management import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-m', '--model_name', type=str, help='Model name')
        parser.add_argument('-s', '--sequence_id', type=int, help='Sequence Id', nargs='+')

    def handle(self, *args, **options):
        model_name = options['model_name']
        sequence_list = options['sequence_id']

        model_ins_list = [model for model in apps.get_models()]
        model_name_list = [model.__name__ for model in apps.get_models()]

        if model_name in model_name_list:
            index = model_name_list.index(model_name)
            model_obj = model_ins_list[index]
            queryset = model_obj._default_manager.all()

            cur_model_ids = list(queryset.values_list('id', flat=True))

            b_set = set(sequence_list)
            updated_sequence_model = [model_obj._default_manager.get(
                id=sequence_list.pop(0)) if x in b_set else model_obj._default_manager.get(id=x) for x
                                      in cur_model_ids]
            for index, y in enumerate(updated_sequence_model):
                y._order = index
                y.save()
