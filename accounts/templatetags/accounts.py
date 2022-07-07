from django import template
register = template.Library()


@register.simple_tag
def parse_result_value(result, field_refer_to):
    if isinstance(result, str):
        return "- -"

    return result.get(field_refer_to, " - - ")
register.filter('parse_result_value', parse_result_value)

@register.simple_tag
def print_value(result):
    print (result, type(result))
    return result
register.filter('print_value', print_value)
