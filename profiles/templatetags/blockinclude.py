from django import template
from django.template.loader_tags import IncludeNode, construct_relative_path

register = template.Library()

BLOCK_CONTEXT_KEY = 'block_context'

@register.tag('blockinclude')
def blockinclude(parser, token):

    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "%r tag takes at least one argument: the name of the template to "
            "be included." % bits[0]
        )

    options = {}
    remaining_bits = bits[2:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise template.TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = template.base.token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise template.TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == 'only':
            value = True
        else:
            raise template.TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value

    isolated_context = options.get('only', False)
    namemap = options.get('with', {})
    bits[1] = construct_relative_path(parser.origin.template_name, bits[1])

    filter_compile = parser.compile_filter(bits[1])

    nodelist = parser.parse(('endblockinclude',))
    parser.delete_first_token()
    
    return BlockIncludeNode(
        nodelist, filter_compile,
        extra_context=namemap,
        isolated_context=isolated_context
    )
 
class BlockIncludeNode(IncludeNode):

    def __init__(self, nodelist, *args, **kwargs):
        self.nodelist = nodelist
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<{self.__class__.__qualname__}: template={self.template!r}>'

    def render(self, context):
        """
        Render the specified template and context. Cache the template object
        in render_context to avoid reparsing and loading when used in a for
        loop.
        """
        template = self.template.resolve(context)
        if not callable(getattr(template, 'render', None)):
            template_name = template or ()
            if isinstance(template_name, str):
                template_name = (template_name,)
            else:
                template_name = tuple(template_name)
            cache = context.render_context.dicts[0].setdefault(self, {})
            template = cache.get(template_name)
            if template is None:
                template = context.template.engine.select_template(template_name)
                cache[template_name] = template
        elif hasattr(template, 'template'):
            template = template.template
        values = {
            name: var.resolve(context)
            for name, var in self.extra_context.items()
        }
        if self.isolated_context:
            context = context.new(values)
        with context.render_context.push_state(template, isolated_context=False):
            return template._render(context)
