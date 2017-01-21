#!/usr/bin/python3
import unittest

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
		self.out_alphabet_back = self.back_alphabet( self.out_alphabet_out )

		self.right, self.left = (None, None)

		self.notch = ord( notch ) - 65
		

	def encode_out(self, code ):
		""" Encypher a code (0-25) through the wiring, on the way out (leftward, toward the reflector)
		
		:param code: the alphabetical position of the letter to be encoded (0-25)
		:return: the alphabetical position of the encyphered letter
		:type code: int
		:rtype: int
		"""
		# Ex. if position is 'B', will return position 1 in encyphered alphabet
		return self.out_alphabet_out[ code ]

	def encode_back(self, code ):
		""" Encypher a code (0-25) through the wiring, on the way back (rightward, back from the reflector)
		
		:param code: the alphabetical position of the letter to be encoded (0-25)
		:return: the alphabetical position of the encyphered letter
		:type code: int
		:rtype: int
		"""
		return self.out_alphabet_back[ code ]

	def set_ring( self, letter ):
		""" Rotate the internal wiring with respect to the letters

		Ex. Ring setting 'A' is the default. Ring setting 'C' rotates the default output alphabet by 2 positions, 
		decreasing the value of each encyphered code by the same amount.
			'EKMFLGDQVZNTOWYHXUSPAIBRCJ' --> 'ELGMOHNIFSXBPVQYAJZWURCKDT'

		:param position: a letter, as a single-character string
		:type position: str
		"""
		position = ord(letter) - 65
		# [2:] + [:1]
		if position == 0:
			self.out_alphabet_out = self.A_ring_setting_alphabet
		else:
			self.out_alphabet_out = self.A_ring_setting_alphabet[-position:] + self.A_ring_setting_alphabet[:-position] 
			print("Alphabet after rotation by {} positions: {}".format( position, self.alphabet()))
			self.out_alphabet_out = [ (code+position)%26 for code in self.out_alphabet_out ]

		self.out_alphabet_back = self.back_alphabet( self.out_alphabet_out )

	def alphabet( self ):
		""" Return the encryption alphabet (leftward encoding), as a human-readable string.

		:return: the alphabet, as scrambled through the wiring
		:rtype: str
		"""
		return ''.join( [ chr(code+65) for code in self.out_alphabet_out ] )

	def back_alphabet( self, out_alphabet ):
		""" From a leftward-encoding alphabet, compute the symmetrical, rightward-encoded alphabet, 
		to be used for the scrambling operations happening on the way back from the reflector.

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

		self.rotor1 = Rotor( 'I',  'EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'Q' )
		self.rotor2 = Rotor( 'II', 'AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E' )
		self.rotor3 = Rotor( 'III','BDFHJLCPRTXVZNYEIWGAKMUSQO', 'V' ) 
		# reflector
		self.reflectorB = Rotor( 'Wide-B', 'YRUHQSLDPXNGOKMIEBFZCWVJAT' )

		# Rotors I through III, from L to R
		self.assemble_rotors( self.rotor1, self.rotor2, self.rotor3, self.reflectorB )

		# Set this attribute to prevent rotor stepping (prevent polyalphabetic encyphering)
		self.STATIC=False

	def assemble_rotors(self, left, middle, right, reflector):
		""" 
		Choose the rotors to be used and arrange them of the shaft.

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

	def step( self, rotor ):
		""" Advance the rotor by one position. If carry notch engages, takes rotor on the left one step further. 

		:param rotor: a rotor (i.e. not a reflector)
		:param rotor: Rotor
		"""
		# Ex. is carry notch is 'Q' and current position is 'Q', the step that is about to occur
		# will take the rotor on the left one step further.
		carry = ( rotor.position == rotor.notch)

		rotor.position += 1

		if rotor.left is not None and rotor.left is not self.reflector and carry:
			step( rotor.left )
				

	def encypher( self, letter ):
		""" Encode a letter, given the Enigma settings (rotor positions, ring settings) currently defined.
		
		:param letter: a single-character string. Ex. 'A'
		:type letter: str
		:return: the encoded letter, as output from a out-and-back scrambling through the 3 rotors and the reflector.
		:rtype: str
		"""

		
		print("Encoding {}".format(letter))
		input_code = ord(letter)-65

		if not self.STATIC:
			self.step( self.rotor_R )

		for rotor in (self.rotor_R, self.rotor_M, self.rotor_L ):
			
			if rotor is self.rotor_R:
				print('Entering rotor {}: {} ({})'.format(rotor.rotor_id, (input_code + rotor.position) %26, chr(input_code + rotor.position +65) ))
				exit_code = rotor.encode_out( ( input_code + rotor.position) % 26 )
			else:
				print('Entering rotor {}: {} ({})'.format(rotor.rotor_id, input_code, chr(input_code + 65) ))
				exit_code = rotor.encode_out( input_code )

			print('Exiting rotor {}: {} ({})'.format(rotor.rotor_id, exit_code, chr(exit_code+65) ))
			input_code = (exit_code - rotor.position + rotor.left.position) % 26

		print('Entering reflector {}: {} ({})'.format(self.reflector.rotor_id, input_code, chr(input_code + 65) ))
		exit_code = self.reflector.encode_out( input_code )
		print('Exiting reflector {}: {} ({})'.format(self.reflector.rotor_id, exit_code, chr(exit_code+65) ))
		input_code = (exit_code + self.reflector.right.position) % 26

		for rotor in (self.rotor_L, self.rotor_M, self.rotor_R ):
			print('Entering rotor {}: {} ({})'.format(rotor.rotor_id, input_code, chr(input_code + 65) ))
			exit_code = rotor.encode_back( input_code )
			print('Exiting rotor {}: {} ({})'.format(rotor.rotor_id, exit_code, chr(exit_code+65) ))
			if rotor is self.rotor_R:
				input_code = (exit_code - rotor.position) % 26
			else:
				input_code = (exit_code - rotor.position + rotor.right.position) % 26
		
		return chr( input_code + 65 )
	




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
		self.enigma.rotor_R.position = 1 # B position
		self.assertEqual( self.enigma.encypher('A'), 'B')
		
	def test_encypher_single_letter_2(self):
		print("\nTest3: static, with rotors in ABB position")
		self.enigma.STATIC = True
		self.enigma.rotor_R.position = 1 # B position
		self.enigma.rotor_M.position = 1 # B position
		self.assertEqual( self.enigma.encypher('A'), 'Y')

	def test_encypher_single_letter_3(self):
		print("\nTest4: static, with rotors in ACB position")
		self.enigma.STATIC = True
		self.enigma.rotor_R.position = 1 # B position
		self.enigma.rotor_M.position = 2 # C position
		self.assertEqual( self.enigma.encypher('A'), 'P')
		
	
	def test_encypher_single_letter_4(self):
		print("\nTest4: static, with rotors in KCB position")
		self.enigma.STATIC = True
		self.enigma.rotor_R.position = 1 # B position
		self.enigma.rotor_M.position = 2 # C position
		self.enigma.rotor_L.position = 10 # K position
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
		self.enigma.rotor1.set_ring('C')

		self.assertEqual( self.enigma.rotor1.alphabet(), 'ELGMOHNIFSXBPVQYAJZWURCKDT' )

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

if __name__ == '__main__':
	unittest.main()

