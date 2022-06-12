import logging
from re import L
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import markdown

positional_defaults = {
  've-style': ['layout', 'theme'],
  've-meta': ['title', 'description'],
  've-image': ['src', 'options', 'seq', 'fit'],
  've-header': ['label', 'background', 'subtitle', 'options', 'position', 'sticky']
}
class_args = {
  've-image': ['sticky']
}
def default(ctx, *args, **kwargs):
  if len(args) > 0:
    _classes = []
    for idx, arg in enumerate(args):
      if ctx.type in class_args and arg in class_args[ctx.type]:
        _classes.append(arg)
      elif ctx.type in positional_defaults and idx < len(positional_defaults[ctx.type]):
        kwargs[positional_defaults[ctx.type][idx]] = arg
    if len(_classes) > 0:
      kwargs['class'] = ' '.join(_classes)
  logger.debug(f'{ctx.type} {kwargs}')
  kwargs = [f'{k}="{v}"' for k,v in kwargs.items()]
  html = f'<{ctx.type} {" ".join(kwargs)}>{markdown.markdown(ctx.content)}</{ctx.type}>'
  return html
