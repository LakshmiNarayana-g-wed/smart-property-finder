from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def rupees(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    if amount == amount.to_integral_value():
        return f'{int(amount):,}'
    return f'{amount:,.2f}'
