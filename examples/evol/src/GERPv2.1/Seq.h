/*
 * Copyright 2007 George Asimenos
 *
 *
 * This file is part of the GERPv2.1 package.
 *
 * GERPv2.1 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * GERPv2.1 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#ifndef SEQ_H
#define SEQ_H

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                               *
 * Seq is the sequence class                                     *
 *                                                               *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

/*
* Notes:
* -----
*
* For several reasons, the sequence starts from 1, not from 0. The character
* at position 0 should be something dummy that we agree on, like '#'. [Actually
* it's BIO::SPECIAL].
*                                                     --George@2004-04-28
*
* Functions that operate on output streams don't mess with their caching properties.
* The user has to hack the streams before passing them to the functions. See the
* implementation of readFromFile(String) for an example of buffered streams.
*                                                     --George@2004-05-03
*/

/* ===========================================================
 * WARNING: THIS FILE IS STILL IN BETA STAGE
 * ===========================================================
 */

#include <fstream>
#include <iostream>
#include "Vec.h"
#include "Constants.h"
using namespace std;

class Seq
{
	friend class Mseq;

	public:
	
	/* Types */
	/* ===== */

	typedef Vec<char>::size_type size_type;
	typedef Vec<char>::iterator iterator;
	typedef Vec<char>::const_iterator const_iterator;
	
	/* Constructors */
	/* ============ */

	/* Empty sequence */
	Seq() : _title(""), _id(0) { _data.resize(0); }

	/* Sequence from filename */
	Seq(string fname, BIO::FileFormat ff = BIO::FF_FASTA);

	/* Sequence from input stream */
	Seq(istream &is, BIO::FileFormat ff = BIO::FF_FASTA);

	/* Sequence copied from a part of another sequence */
	// Optional parameter BIO::SeqFlags may be some combination (ORed together) of:
	//    - BIO::FLAG_REVERSE
	//    - BIO::FLAG_COMPLEMENT
	Seq(Seq &from, size_type start, size_type num, BIO::SeqFlags flags = BIO::FLAG_NONE);

	/* Sequence created from alignment */
	//
	// Given an Vec<char> containing the skeleton for an
	// alignment and the identity of the current character, this
	// routine will create a new sequence with all necesssary gaps added.
	// For instance,
	//    from = "ATGCAGTCA"
	//    alignment = "XXXBBYYYBBYYXX"
	//    me = 'X'
	// will perform the transformation
	//    "ATGCAGTCA" --> "ATGCC---GT--CA"
	//                    (XXXBBYYYBBYYXX)
	//
	// 'X', 'Y' and 'B' are defined in Constants.h as BIO::ALIGN_X, ALIGN_Y, ALIGN_BOTH
	Seq(Seq &from, Vec<char> &alignment, char me);
	
	/* Methods */
	/* ======= */

	/* Get attributes */
	size_type getLength() const;
	string getTitle() const;
	unsigned int getID() const;
	
	char getLetter(size_type index) const; //return letter from a certain position
	iterator getBegin(); //return an iterator @ the beginning <--- preferred method for going through sequence
	iterator getIterator(size_type index); //return an iterator @ a specific index
	iterator getEnd(); //return an iterator @ the end.
	const_iterator getBegin() const; //return a const iterator @ the beginning <--- preferred method for going through sequence
	const_iterator getIterator(size_type index) const; //return a const iterator @ a specific index
	const_iterator getEnd() const; //return a const iterator @ the end.
	size_type countLetters() const; //count the letters (length of sequence not counting the gaps)

	/* Set attributes */
	void setTitle(string s);
	void setID(unsigned int i);
	void changeLetter(char letter, size_type index);

	/* In-place transformations of the sequence */
	void rotate(size_type shift); // Rotate sequence to the right by 'shift' letters

	/* Misc */
	void writeASCII(ostream &os = cout); //dump the sequence's letters
	
	void writeToFile(ostream &os, BIO::FileFormat ff = BIO::FF_FASTA, unsigned int width = 78, bool useID = false); //write to file
	// currently only BIO::FF_FASTA (as a FileFormat) makes sense here, with a specified width.
	// defaults: width=78, useID=false (i.e. dump title instead of ID as FASTA header)

	/* Constructor-like methods */
	void clear(); //like empty constructor
	void readFromFile(string fname, BIO::FileFormat ff = BIO::FF_FASTA); //like filename constructor
	void readFromFile(istream &is, BIO::FileFormat ff = BIO::FF_FASTA); //like input stream constructor
	void copyFrom(Seq &from, size_type start, size_type num); //like copy constructor
	void alignFrom(Seq &from, Vec<char> &alignment, char me); //like alignment constructor
	
	/* TODO: getMappingVec()? getHighlight()? */

	/* Operators */
	/* ========= */

	char &operator[](size_type index); //reference a single letter using []
	const char &operator[](size_type index) const; //get a single letter using []
	friend ostream &operator<<(ostream &os, Seq &s); //output using writeASCII
	
	private:
		
	/* The letters vector */
	Vec<char> _data;
	
	/* The title of the sequence */
	string _title;
	
	/* An integer ID of the sequence */
	unsigned int _id;

	/* Code shared between constructors and constructor-like methods */
	void _readFromFile(string fname, BIO::FileFormat ff);
	void _readFromFile(istream &is, BIO::FileFormat ff);
	void _copyFrom(Seq &from, size_type start, size_type num, BIO::SeqFlags flags = BIO::FLAG_NONE);
	void _alignFrom(Seq &from, Vec<char> &alignment, char me);
};

#endif
