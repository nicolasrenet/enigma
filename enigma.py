#!/usr/bin/python3
import unittest

LOGLEVEL=2

def log( content, level=3):
	if level <= LOGLEVEL:
		print(content)
	

class Rotor():
	
	def __init__(self, rotor_id, out_alphabet, notch='%'):
		""" Create a new rotor.

		:param rotor_id: the string that identifies the rotor wiring, usually a Roman numeral (I, II, III, ...)
		:param out_alphabet: the scrambled sequence of letters obtained from the alphabetical sequence 'ABC..XYZ'
		:param notch: the position of the turnover notch, expressed as a 1-letter string Ex. Q
		:type rotor_id: str
		:type out_alphabet: str
		:type notch: str
		"""
		self.rotor_id = rotor_id
		self.position = 0 # 'A' position
		# alphabets are coded with the corresponding ordinals (0-25)
		
		# This is not meant to change
		self.A_ring_setting_alphabet = [ ord(letter)-65 for letter in list( out_alphabet ) ]

		self.out_alphabet_out = self.A_ring_setting_alphabet
		# reverse mapping for encoding on the way back from reflector
		self.out_alphabet_back = self._back_alphabet( self.out_alphabet_out )

		self.right, self.left = (None, None)

		self.notch = ord( notch ) - 65

		self.ring_setting = 0
		

	def encode_out(self, code ):
		""" Encypher a code (0-25) through the wiring, on the way out (leftward, toward the reflector).
		
		:param code: the alphabetical position of the letter to be encoded (0-25)
		:return: the alphabetical position of the encyphered letter
		:type code: int
		:rtype: int
		"""
		# Ex. if position is 'B', will return position 1 in encyphered alphabet
		return self.out_alphabet_out[ code ]

	def encode_back(self, code ):
		""" Encypher a code (0-25) through the wiring, on the way back (rightward, back from the reflector).
		
		:param code: the alphabetical position of the letter to be encoded (0-25)
		:return: the alphabetical position of the encyphered letter
		:type code: int
		:rtype: int
		"""
		return self.out_alphabet_back[ code ]
	
	def set_position(self, letter ):
		""" Set the starting position for the rotor, given a letter code.

		:param letter: a one-character string.
		:type letter: str
		"""
		self.position = ord(letter)-65

	def get_position(self):
		""" Return the position of the rotor in human-readable form, i.e. as a letter.

		:return: a single-letter letter string.
		:rtype: str
		"""
		return chr(self.position+65)

	def increment_position(self):
		""" Take the rotor one step further, without considering the turnover notch.
		"""
		self.position = (self.position + 1)%26

	def set_ring( self, letter ):
		""" Rotate the internal wiring with respect to the letters ring.

		Ex. Ring setting 'A' is the default. Ring setting 'C' rotates the default output alphabet by 2 positions, 
		increasing the value of each encyphered code by the same amount.
			'EKMFLGDQVZNTOWYHXUSPAIBRCJ' --> 'ELGMOHNIFSXBPVQYAJZWURCKDT'

		:param letter: a letter, as a single-character string
		:type letter: str
		"""
		self.ring_setting = ord(letter) - 65

		if self.ring_setting == 0:
			self.out_alphabet_out = self.A_ring_setting_alphabet
		else:
			self.out_alphabet_out = self.A_ring_setting_alphabet[-self.ring_setting:] + self.A_ring_setting_alphabet[:-self.ring_setting] 
			log("Alphabet after rotation by {} self.ring_settings: {}".format( self.ring_setting, self.alphabet()))
			self.out_alphabet_out = [ (code+self.ring_setting)%26 for code in self.out_alphabet_out ]

		self.out_alphabet_back = self._back_alphabet( self.out_alphabet_out )

	def get_ring_setting( self ):
		""" Return the ring setting for the rotor in human-readable form, i.e. as a letter.

		:return: a single-letter letter string.
		:rtype: str
		"""
		return chr(self.ring_setting+65)

	def get_window_letter( self ):
		""" Return the letter that appears in the 3-letter window.

		The letter is obtained by adding the ring setting offset to the current rotor position.

		:return: a single-letter string.
		:rtype: str
		"""
		return chr( self.position + self.ring_setting + 65)

	def get_window_numeral( self ):
		""" Return the numeric value of the letter that appears in the window.

		:return: a integer between 0 and 25
		:rtype: int
		"""
		return self.position + self.ring_setting


	def alphabet( self ):
		""" Return the encryption alphabet (leftward encoding), as a human-readable string.

		:return: the alphabet, as scrambled through the wiring
		:rtype: str
		"""
		return ''.join( [ chr(code+65) for code in self.out_alphabet_out ] )

	def _back_alphabet( self, out_alphabet ):
		""" From a leftward-encoding alphabet, compute the symmetrical, rightward-encoded alphabet, to be used for the scrambling operations happening on the way back from the reflector.

		:param out_alphabet: the leftward-encoding alphabet, that uniquely defines the wiring of the rotor, represented as an array of letter positions (0-25)
		:type out_alphabet: list
		:return: the rightward-encoding alphabet, as an array of letter positions (0-25)
		:rtype: list
		"""

		back_alph = [ 0 for i in range(26) ]
		for character_position in out_alphabet:
			back_alph[ out_alphabet[ character_position] ] = character_position
		return back_alph
		

class Enigma():


	def __init__(self):
		""" Create a new Enigma machine.

		Default settings:
		 * 3 rotors: I, II, III (in this order)
		 * Wide-B reflector
		 * rotor positions: AAA
		 * ring setting: AAA
		 """

		self.rotors = [ Rotor( 'I',  'EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'Q' ), 
				Rotor( 'II', 'AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E' ),
				Rotor( 'III','BDFHJLCPRTXVZNYEIWGAKMUSQO', 'V' ),
				Rotor( 'IV', 'ESOVPZJAYQUIRHXLNFTGKDCMWB', 'J' ),
				Rotor( 'V',  'VZBRGITYUPSDNHLXAWMJQOFECK', 'Z' )
				]
		# reflector
		self.reflectorB = Rotor( 'Wide-B', 'YRUHQSLDPXNGOKMIEBFZCWVJAT' )

		# Rotors I through III, from L to R
		self._assemble_rotors( self.rotors[0], self.rotors[1], self.rotors[2], self.reflectorB )

		# Set this attribute to prevent rotor stepping (prevent polyalphabetic encyphering)
		self.STATIC=False

	def _assemble_rotors(self, left, middle, right, reflector):
		""" 
		Choose the rotors to be used and arrange them on the shaft.

		:param left: the leftmost rotor, next to the reflector
		:param middle: the middle rotor
		:param right: the rightmost rotor
		:param reflector: the reflector
		"""	
		self.rotor_L = left
		self.rotor_M = middle
		self.rotor_R = right
		self.reflector = reflector


		self.rotor_R.left = self.rotor_M
		self.rotor_M.left = self.rotor_L
		self.rotor_L.left = self.reflector
		self.reflector.right = self.rotor_L
		self.rotor_L.right = self.rotor_M
		self.rotor_M.right = self.rotor_R

	def set_positions(self, trigram ):
		""" Set the start position for the rotors, given a 3-letter code.
		
		:param trigram: the 3-letter code for the rotor positions, where letters 1, 2, and 3 correspond to the L, M, and R rotors, respectively.
		:type trigram: str
		"""
		self.rotor_L.set_position( trigram[0] )
		self.rotor_M.set_position( trigram[1] )
		self.rotor_R.set_position( trigram[2] )

	def get_window( self ):
		""" Return the 3-letter "window", i.e. the current position for the 3 rotors (with an offset, if the ring setting is 1 or more). 

		:return: a 3-letter string, representing the positions of the left, middle, and right rotors, respectively, with the offset created by the ring setting.
		:rtype: str
		"""
		return ''.join( [ self.rotor_L.get_window_letter() , self.rotor_M.get_window_letter(), self.rotor_R.get_window_letter() ])

	def get_positions(self):
		""" Return the current position for the 3 rotors, as a trigram.

		:return: a 3-letter string, representing the positions of the left, middle, and right rotors, respectively.
		:rtype: str
		"""
		return ''.join( [ self.rotor_L.get_position() , self.rotor_M.get_position(), self.rotor_R.get_position() ])

	def set_rings(self, trigram ):
		""" Set the rings, given a 3-letter code.
		
		:param trigram: the 3-letter code for the ring positions, where letters 1, 2, and 3 correspond to the L, M, and R rotors, respectively.
		:type trigram: str
		"""

		self.rotor_L.set_ring( trigram[0] )
		self.rotor_M.set_ring( trigram[1] )
		self.rotor_R.set_ring( trigram[2] )

	def configure(self, rotor_selection='123', rotor_positions='AAA', ring_settings='AAA' ):
		""" Define the initial configuration of the machine.

		:param rotor_positions: a 3-letter code that determines the starting position for the rotors
		:param ring_settings: a 3-letter code that determines the ring settings for the rotors
		:type rotor_positions: str
		:type ring_settings: str
		"""
		left_rotor = self.rotors[ int(rotor_selection[0])-1 ]
		middle_rotor = self.rotors[ int(rotor_selection[1])-1 ]
		right_rotor = self.rotors[ int(rotor_selection[2])-1 ]

		self._assemble_rotors( left_rotor, middle_rotor, right_rotor, self.reflectorB )

		self.set_positions( rotor_positions )
		self.set_rings( ring_settings )

	def step( self, rotor ):
		""" Advance the rotor by one position. If carry notch engages (in the "turnover" position), takes rotor on the left one step further. 

		:param rotor: a rotor (i.e. not a reflector)
		:type rotor: Rotor
		"""
		# Ex. is carry notch for the rotor is 'Q' and current position is 'Q', the step that is about to occur
		# will also take the rotor on the left one step further.
		carry = (rotor.get_window_numeral() == rotor.notch)

		rotor.increment_position()

		if rotor.left is not None and rotor.left is not self.reflector and carry:
			log("TURNOVER from rotor {} to rotor {}".format( rotor.rotor_id, rotor.left.rotor_id ),2)
			self.step( rotor.left )
				

	def encypher( self, letter ):
		""" Encode a letter, using the Enigma settings (rotor positions, ring settings) currently defined.
		
		:param letter: a single-character string. Ex. 'A'
		:type letter: str
		:return: the encoded letter, as output from a out-and-back scrambling through the 3 rotors and the reflector.
		:rtype: str
		"""

		log("Encoding {}".format(letter),2)
		input_code = ord(letter)-65

		if not self.STATIC:
			self.step( self.rotor_R )

		log('Position:  {} Window: {}'.format( self.get_positions(), self.get_window()), 2)	

		# The way out of the leftmost rotor, to the reflector
		for rotor in (self.rotor_R, self.rotor_M, self.rotor_L ):
			
			if rotor is self.rotor_R:
				log('Entering rotor {}: {} ({})'.format(rotor.rotor_id, (input_code + rotor.position) %26, chr(input_code + rotor.position +65) ))
				exit_code = rotor.encode_out( ( input_code + rotor.position) % 26 )
			else:
				log('Entering rotor {}: {} ({})'.format(rotor.rotor_id, input_code, chr(input_code + 65) ))
				exit_code = rotor.encode_out( input_code )

			log('Exiting rotor {}: {} ({})'.format(rotor.rotor_id, exit_code, chr(exit_code+65) ))
			input_code = (exit_code - rotor.position + rotor.left.position) % 26

		# Turnaround in the reflector
		log('Entering reflector {}: {} ({})'.format(self.reflector.rotor_id, input_code, chr(input_code + 65) ))
		exit_code = self.reflector.encode_out( input_code )
		log('Exiting reflector {}: {} ({})'.format(self.reflector.rotor_id, exit_code, chr(exit_code+65) ))
		input_code = (exit_code + self.reflector.right.position) % 26

		# The way back to the rightmost rotor
		for rotor in (self.rotor_L, self.rotor_M, self.rotor_R ):
			log('Entering rotor {}: {} ({})'.format(rotor.rotor_id, input_code, chr(input_code + 65) ))
			exit_code = rotor.encode_back( input_code )
			log('Exiting rotor {}: {} ({})'.format(rotor.rotor_id, exit_code, chr(exit_code+65) ))
			if rotor is self.rotor_R:
				input_code = (exit_code - rotor.position) % 26
			else:
				input_code = (exit_code - rotor.position + rotor.right.position) % 26
		
		encyphered_letter = chr( input_code + 65 )
		log('--> encyphered: ' + encyphered_letter, 2 )
		return encyphered_letter
	
	def message( self ):
		"""Interact with the machine: allow for configuring a machine (rotors selection, rotors positions and ring settings), and for encoding an entire message, or letter by letter.
		"""

		rotor_selection = input("Choose the rotors to be used, from left to right [default: 123 ]: ")
		if rotor_selection == '': rotor_selection = '123' 
		rotor_position = input("Choose the starting positions for the rotors [default: 'AAA']: ")
		if rotor_position == '': rotor_position = 'AAA'
		ring_setting = input("Choose the ring settings for the rotors [default: 'AAA']: ")
		if ring_setting == '': ring_setting = 'AAA'
		interactive = input("Interactive mode? [N/y] ")
		if interactive == '': interactive = False

		self.configure( rotor_selection, rotor_position, ring_setting)

		if interactive:

			to_encode = ''
			while( to_encode != 'quit()' ):
				to_encode = input("Enter a letter: ")
				print( self.encypher( to_encode ) )
		else:
			message = input("Enter the message: " )
			cleaned_up_message =  message.translate(str.maketrans('','',' .,;:?!@%+-_\'')).upper()
			encoded_message = []
			for letter in list( cleaned_up_message ):
				encoded_message.append( self.encypher( letter ))
			print( cleaned_up_message )
			print(''.join( encoded_message ) )

	

class TestRotors( unittest.TestCase ):

	def setUp(self):
		self.enigma = Enigma()
		

	def test_encypher_single_letter_AAA(self):
		print("\nTest 1: STATIC, with rotors in AAA position")
		self.enigma.STATIC = True
		self.assertEqual( self.enigma.encypher('A'), 'U')
		self.assertEqual( self.enigma.encypher('G'), 'P')
		self.assertEqual( self.enigma.encypher('P'), 'G')

	def test_encypher_single_letter_1(self):
		print("\nTest 2: STATIC, with rotors in AAB position")
		self.enigma.STATIC = True
		self.enigma.rotor_R.set_position('B') # B position
		self.assertEqual( self.enigma.encypher('A'), 'B')
		
	def test_encypher_single_letter_2(self):
		print("\nTest3: static, with rotors in ABB position")
		self.enigma.STATIC = True
		self.enigma.rotor_R.set_position('B') # B position
		self.enigma.rotor_M.set_position('B') # B position
		self.assertEqual( self.enigma.encypher('A'), 'Y')

	def test_encypher_single_letter_3(self):
		print("\nTest4: static, with rotors in ACB position")
		self.enigma.STATIC = True
		self.enigma.rotor_R.set_position('B') # B position
		self.enigma.rotor_M.set_position('C')  # C position
		self.assertEqual( self.enigma.encypher('A'), 'P')
		
	
	def test_encypher_single_letter_4(self):
		print("\nTest4: static, with rotors in KCB position")
		self.enigma.STATIC = True
		self.enigma.rotor_R.set_position('B') # B position
		self.enigma.rotor_M.set_position('C') # C position
		self.enigma.rotor_L.set_position('K') # K position
		self.assertEqual( self.enigma.encypher('A'), 'R')
		
	
	def test_encypher_polyalphabetic_1(self):
		print("\nTest polyalphabetic sequential encoding, with R-rotor only")
		encyphered_sequence =  [
				self.enigma.encypher('A'),
				self.enigma.encypher('A'),
				self.enigma.encypher('A'),
				self.enigma.encypher('A'), 
				self.enigma.encypher('A') ]

		self.assertEqual( encyphered_sequence, [ 'B', 'D', 'Z', 'G', 'O' ])

	def test_ring_setting_1( self ):
		print("\nTest that ring setting 'C' rotates the alphabet by 2 positions (for rotor I)")
		self.enigma.rotors[0].set_ring('C')

		self.assertEqual( self.enigma.rotors[0].alphabet(), 'ELGMOHNIFSXBPVQYAJZWURCKDT' )

	def test_ring_setting_2( self ):
		print("\nTest polyalphabetic sequential encoding, with R-rotor only and ring setting 'BBB'")

		self.enigma.rotor_L.set_ring('B')
		self.enigma.rotor_M.set_ring('B')
		self.enigma.rotor_R.set_ring('B')

		for rotor in ( self.enigma.rotor_L,  self.enigma.rotor_M,  self.enigma.rotor_R ):
			print( rotor.alphabet() )


		encyphered_sequence =  [
				self.enigma.encypher('A'),
				self.enigma.encypher('A'),
				self.enigma.encypher('A'),
				self.enigma.encypher('A'), 
				self.enigma.encypher('A') ]

		self.assertEqual( encyphered_sequence, [ 'E', 'W', 'T', 'Y', 'X'] )

	def test_configure_positions( self ):
		self.enigma.configure('123', "BCL" )
		
		self.assertEqual( self.enigma.rotor_L.get_position(), 'B')
		self.assertEqual( self.enigma.rotor_M.get_position(), 'C')
		self.assertEqual( self.enigma.rotor_R.get_position(), 'L')


	def test_configure_ring_settings( self ):
		self.enigma.configure('123', ring_settings="FKW" )
		
		self.assertEqual( self.enigma.rotor_L.get_ring_setting(), 'F')
		self.assertEqual( self.enigma.rotor_M.get_ring_setting(), 'K')
		self.assertEqual( self.enigma.rotor_R.get_ring_setting(), 'W')

	def test_middle_rotor_turnover( self ):
		# R-rotor ring is in the notch position
		self.enigma.configure('123','AAV')
		self.enigma.step( self.enigma.rotor_R )
		self.assertEqual( self.enigma.rotor_M.get_position(), 'B') 

	def test_middle_rotor_turnover_with_ring_offset( self ):
		print("Testing that turnover mechanism is triggered by the alphabet ring's position, not the rotor's")
		# R-rotor ring is in the notch position
		self.enigma.configure('123','AAA','AAV')
		self.enigma.step( self.enigma.rotor_R )
		self.assertEqual( self.enigma.rotor_R.get_window_letter(), 'W') 
		self.assertEqual( self.enigma.rotor_M.get_window_letter(), 'B') 

	def test_left_rotor_turnover( self ):
		# M-rotor is in the notch position
		self.enigma.configure('123','AEA')
		self.enigma.step( self.enigma.rotor_M )
		self.assertEqual( self.enigma.rotor_L.get_position(), 'B') 

	def test_left_rotor_turnover_with_ring_offset( self ):
		print("Testing that turnover mechanism is triggered by the alphabet ring's position, not the rotor's")
		# M-rotor is in the notch position
		self.enigma.configure('123','AAA','AEA')
		self.enigma.step( self.enigma.rotor_M )
		self.assertEqual( self.enigma.rotor_M.get_window_letter(), 'F') 
		self.assertEqual( self.enigma.rotor_L.get_window_letter(), 'B') 

	def test_turnover_sequence( self ):
		# R- and M-rotor are in the notch position
		# L-rotor should be taken one step further.
		self.enigma.configure('123','AEV')
		self.enigma.step( self.enigma.rotor_R )
		self.assertEqual( self.enigma.rotor_R.get_position(), 'W') 
		self.assertEqual( self.enigma.rotor_M.get_position(), 'F') 
		self.assertEqual( self.enigma.rotor_L.get_position(), 'B') 

	def test_turnover_sequence_with_ring_offset( self ):
		print("Testing that turnover mechanism is triggered by the alphabet ring's position, not the rotor's")
		# R- and M-rotor are in the notch position
		# L-rotor should be taken one step further.
		self.enigma.configure('123','AAA', 'AEV')
		self.enigma.step( self.enigma.rotor_R )
		self.assertEqual( self.enigma.rotor_R.get_window_letter(), 'W') 
		self.assertEqual( self.enigma.rotor_M.get_window_letter(), 'F') 
		self.assertEqual( self.enigma.rotor_L.get_window_letter(), 'B') 


if __name__ == '__main__':
	unittest.main()

