from typing import List

from django import template
from django.db.models import Q

from claim_application.models import Page, PageField, ApplicationDocumentLog, ClaimantFields, FieldScore, \
    TemporaryValidation, ValidationRuleEngine, Claimant
from master.models import MasterField, DigitalMasterField

register = template.Library()


@register.filter(name='get_page_active_fields')
def _get_page_active_fields(page: Page):
    """
        Get active page fields for the given page and not including image data type
    """
    if page:
        data = (PageField.objects.select_related('master_field', 'page').filter(page=page,
                                                                                is_active=True,
                                                                                master_field__is_active=True).exclude(
            master_field__data_type=MasterField.IMAGE).order_by
                ('master_field__order'))
        return data
    else:
        return []


@register.filter(name='get_image_url')
def _get_image_url(pagefield: PageField):
    try:
        url = ''
        if pagefield:
            if pagefield.value_image:
                url = pagefield.value_image.url
            return url
        else:
            return None
    except Exception as e:
        print("Error: ", str(e))
        return None


@register.filter(name='format_value_text')
def _format_value_text(value):
    if value is not None:
        return value
    else:
        return ''


@register.filter(name='has_group')
def has_group(user, group_name):
    if user.groups.filter(name__in=group_name.split(',')).exists():
        return True
    else:
        return False


@register.filter(name='get_last_document_logs')
def _get_last_document_logs(logs):
    try:
        data = []
        code_list = []
        for log in logs:
            if log.code not in code_list:
                code_list.append(log.code)
                data.append(log)
        data.reverse()
        return data
    except Exception as e:
        print(str(e))
        return []


@register.filter(name='get_page_field_based_on_master_field')
def _get_page_field_based_on_master_field(masterfield: MasterField, page: Page):
    if page:
        data = PageField.objects.filter(page=page,
                                        is_active=True,
                                        master_field=masterfield).first()
        return data
    else:
        return []


@register.filter(name='get_score_field_based_on_master_field')
def _get_score_field_based_on_master_field(masterfield: MasterField, page: Page):
    if page and DigitalMasterField.objects.filter(code=masterfield.code, is_active=True, do_scoring=True).exists():
        data = FieldScore.objects.filter(page=page,
                                         master_field=masterfield).first()
        return data
    else:
        return []


@register.filter(name='get_claimant_field_based_on_master_field')
def _get_claimant_field_based_on_master_field(masterfield: MasterField, page: Page):
    if page:
        claimant_field = ClaimantFields.objects.filter(claimant=page.claimant,
                                                       digital_master_field__code=masterfield.code).first()
        return claimant_field
    else:
        return []


@register.filter(name='get_field_validation')
def _get_field_validation(masterfield: MasterField, page: Page):
    """
        Get a field validation.
    """
    if page and masterfield:
        return TemporaryValidation.objects.filter(field=masterfield, page=page)
    else:
        return None


@register.filter(name='get_page_validation')
def _get_page_validation(page: Page):
    """
        Get page validation.
    """
    if page:
        return TemporaryValidation.objects.filter(page=page, field__isnull=True)
    else:
        return None


@register.filter(name='is_all_mandatory_validation_flag_true')
def _is_all_mandatory_validation_flag_true(temp_validations: List[TemporaryValidation]):
    """
        return True if all mandatory validation for the field is on success.
    """
    if temp_validations:
        return temp_validations.filter(rule__validation_action=ValidationRuleEngine.MANDATORY,
                                       status=TemporaryValidation.SUCCESS).exists()
    else:
        return False


@register.filter(name='fetch_only_two')
def _fetch_only_two(data):
    if len(data) > 2:
        return data[:2]
    return data


@register.filter(name='is_claimant_present')
def _is_claimant_present(pages: list[Page]):
    if pages:
        return pages.filter(
            Q(claimant__isnull=False) | Q(
                page_labels__master_page_label__code='claim_form',
                page_labels__master_page_label__is_active=True
            )
        ).exists()
    return False


@register.filter(name='get_page_validation_score')
def _get_page_validation_score(page_obj: Page, status):
    if page_obj and status:
        return TemporaryValidation.objects.filter(page=page_obj, status=status).count()
    return None


@register.filter(name='filter_text')
def _filter_text(string):
    if string == '' or string is None:
        return '--'
    return string


@register.filter(name='get_front_page_number')
def _get_front_page_number(page: Page):
    """
        Get page number from the front field.
        First check if a page has full view if not then it check for front available or not.
    """
    field_obj = page.pagefields.filter(master_field__code='front').first()
    full_img_obj = page.pagefields.filter(master_field__code='full').first()
    if full_img_obj and full_img_obj.original_page_number:
        return full_img_obj.original_page_number
    elif field_obj and field_obj.original_page_number:
        return field_obj.original_page_number
    return ""


@register.filter(name='get_back_page_number')
def _get_back_page_number(page: Page):
    """
        Get page number from the back field.
        First check if a page has full view if not then it check for back available or not.
    """
    field_obj = page.pagefields.filter(master_field__code='back').first()
    full_img_obj = page.pagefields.filter(master_field__code='full').first()
    if full_img_obj and full_img_obj.original_page_number:
        return full_img_obj.original_page_number
    elif field_obj and field_obj.original_page_number:
        return field_obj.original_page_number
    return ""


@register.filter(name='if_f_b_validation_available')
def _if_f_b_validation_available(page: Page) -> bool:
    """
        It check is CBV001 (Front & Back availability validation) is available to page.
    """
    return TemporaryValidation.objects.filter(page=page, rule__validation_code='CBV001').exists()


@register.filter(name='get_claimform_page')
def _get_claimform_page(pages: List[Page]) -> List[dict]:
    """
        Get all the pages whoes label are claim form.
    """
    return pages.filter(page_labels__master_page_label__code='claim_form',
                        page_labels__master_page_label__is_active=True)


@register.filter(name='get_other_page')
def _get_other_pages(document) -> List:
    data = []
    try:
        data = document.pages.filter(
            (Q(claimant__type=Claimant.HOLDER) & Q(page_labels__master_page_label__is_active=True)) | Q(
                claimant=None)).exclude(
            page_labels__master_page_label__code__in=['other', 'claim_form']).distinct()
    except Exception as e:
        print(str(e))
    return data
