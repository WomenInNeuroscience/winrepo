from django import template
from django.template.loader_tags import BlockNode, IncludeNode, construct_relative_path

register = template.Library()

BLOCK_CONTEXT_KEY = 'block_context'


def get_blocks(nodelist):
    for nl in nodelist:
        if isinstance(nl, BlockNode):
            yield nl
            continue

        for attr in nl.child_nodelists:
            nodelist = getattr(nl, attr, None)
            if nodelist:
                yield from get_blocks(nodelist)


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

    blocks_renaming = {}

    for nl in get_blocks(nodelist):
        if nl.name in parser.__loaded_blocks:
            parser.__loaded_blocks.remove(nl.name)

        idx = 1
        name = nl.name + '_' + str(idx)
        while name in parser.__loaded_blocks:
            idx += 1
            name = nl.name + '_' + str(idx)

        blocks_renaming[nl.name] = name
        nl.name = name

        parser.__loaded_blocks.append(nl.name)

    return BlockIncludeNode(
        nodelist, filter_compile,
        extra_context=namemap,
        isolated_context=isolated_context,
        blocks_renaming=blocks_renaming
    )

class BlockIncludeNode(IncludeNode):

    def __init__(self, nodelist, *args, **kwargs):
        self.nodelist = nodelist
        self.blocks_renaming = kwargs.pop('blocks_renaming', {})
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

        for nl in get_blocks(template.nodelist):
            if not isinstance(nl, BlockNode):
                continue
            if nl.name in self.blocks_renaming:
                nl.name = self.blocks_renaming[nl.name]

        values = {
            name: var.resolve(context)
            for name, var in self.extra_context.items()
        }
        if self.isolated_context:
            context = context.new(values)
        else:
            context.update(values)
        with context.render_context.push_state(template, isolated_context=False):
            return template._render(context)
