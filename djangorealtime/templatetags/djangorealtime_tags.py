from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@lru_cache(maxsize=1)
def _get_js_content():
    """Read and cache the JavaScript content"""
    js_path = Path(__file__).parent.parent / 'static' / 'djangorealtime' / 'js' / 'realtime.js'
    return js_path.read_text()

@register.simple_tag
def djangorealtime_js(auto_connect=True):
    """Include the DjangoRealtime JavaScript library (inline from file)

    Args:
        auto_connect: Whether to automatically connect on page load (default: True)
    """
    # In debug mode, clear cache to always read fresh content
    if settings.DEBUG:
        _get_js_content.cache_clear()

    js_content = _get_js_content()

    auto_connect_str = 'true' if auto_connect else 'false'
    js_content_with_config = js_content.replace('__AUTO_CONNECT__', auto_connect_str)

    return mark_safe(f'<script id="djangorealtime-js">\n{js_content_with_config}\n</script>')

@register.simple_tag
def djangorealtime_init(endpoint='/realtime/sse/', debug=False):
    """Initialize DjangoRealtime connection with optional configuration"""
    debug_str = 'true' if debug else 'false'
    script = f"""
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            window.djangoRealtimeConnection = DjangoRealtime.connect({{
                endpoint: '{endpoint}',
                debug: {debug_str},
                onConnect: function() {{
                    console.log('DjangoRealtime connected');
                }},
                onMessage: function(data) {{
                    // Default message handler - can be overridden
                }},
                onError: function(error) {{
                    console.error('DjangoRealtime connection error:', error);
                }}
            }});
        }});
    </script>
    """
    return mark_safe(script)
