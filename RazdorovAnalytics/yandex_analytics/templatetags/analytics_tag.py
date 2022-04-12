from django import template

register = template.Library()

@register.simple_tag
def calc(expression):
    allowed = '+-/*'
    for sign in allowed:
        if sign in expression:
            try:
                left,right = expression.split(sign)
                left,right = int(left),int(right)
                if sign =='+':
                    return left+right
                elif sign == "-":
                    return left-right
                elif sign == "*":
                    return left * right
                elif sign == "/":
                    return left/right
            except(ValueError,TypeError):
                raise ValueError('Ошибка')
