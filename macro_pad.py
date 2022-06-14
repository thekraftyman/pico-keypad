# macro_pad.py

from pad import Keypad
from types import FunctionType

class MacroPad( Keypad ):
	def __init__( self, **kwargs ):
		''' macro pad based on the pico keypad '''
		super().__init__( **kwargs )
		self._bindings = {}

	@property
	def bindings( self ):
		''' dictionary where key bindings are defined '''
		return self._bindings

	def bind_key( self, key_num, callback ):
		'''
		Binds a callback function a key to run when the key is pressed

		:arg int key_num: key int val to bind
		:arg FunctionType callback: function to call when the key is pressed
		'''
		# do some error checking
		assert type( callback ) == FunctionType
		key_num = int( key_num )
		self.check_key( key_num )
		if key_num in self._bindings:
			raise Exception( f"Key {key_num} is already bound to a function. Use the `drop_key` function to release the binding before rebinding the key" )

		# bind the key
		self._bindings[ key_num ] = callback

	def call( self, key_num, **kwargs ):
		'''
		call a function from the bindings

		:arg int key_num: key int val to call
		'''
		# do some error checking
		key_num = int( key_num )
		self.check_key( key_num )

		# run the function
		self._bindings[ key_num ]( **kwargs )

	def drop_key( self, key_num ):
		'''
		Remove binding on a given key

		:arg int key_num: key int val to drop from bindings
		'''
		# do some error checking
		key_num = int( key_num )
		self.check_key( key_num )
		if key_num not in self._bindings:
			return

		# remove the bound function
		func = self._bindings.pop( key_num )
