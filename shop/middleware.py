from django.templatetags.static import static
from django.utils.functional import cached_property


class AdminCopilotAssetsMiddleware:
	"""Inject Copilot assets on every staff HTML response under /admin/."""

	@cached_property
	def _injection(self):
		css = static('admin_copilot.css')
		js = static('admin_copilot.js')
		return (
			f'<link rel="stylesheet" href="{css}?v=20260603-all-admin">'
			f'<script src="{js}?v=20260603-all-admin" defer></script>'
		).encode('utf-8')

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)

		if not getattr(request, 'user', None) or not request.user.is_staff:
			return response

		if not request.path.startswith('/admin'):
			return response

		content_type = response.get('Content-Type', '')
		if 'text/html' not in content_type:
			return response

		if hasattr(response, 'render'):
			response.render()

		if not hasattr(response, 'content'):
			return response

		if b'mimosa-copilot-tab' in response.content:
			return response

		if b'</body>' not in response.content:
			return response

		response.content = response.content.replace(
			b'</body>',
			self._injection + b'</body>',
			1,
		)
		if 'Content-Length' in response:
			del response['Content-Length']

		return response
