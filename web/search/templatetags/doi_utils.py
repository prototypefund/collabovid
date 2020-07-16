from django import template
register = template.Library()

@register.filter()
def extract_arxiv_id(value):
    return value.replace('arXiv:', '')

@register.filter()
def is_arxiv(paper):
    print(paper.host.name)
    return paper.host.name == 'arXiv'