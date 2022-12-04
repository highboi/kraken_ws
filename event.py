#a class for events in python
class Event():
	def __init__(self):
		self.handlers = []

	def __iadd__(self, handler):
		self.handlers.append(handler)
		return self

	def __isub__(self, handler):
		self.handlers.remove(handler)
		return self

	def __call__(self, sender, earg=None):
		for handler in self.handlers:
			handler()
			self.remove(handler)
