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

/* =====================================================
 * WARNING: THIS FILE IS STILL IN BETA STAGE
 * =====================================================
 *
 * See Seq.h for more info
 *
 */

#include "Seq.h"
#include <cassert>
#include <cctype>
#include <iostream>
#include <algorithm>

using namespace std;

Seq::Seq(string fname, BIO::FileFormat ff) : _id(0)
{
	_readFromFile(fname, ff);
}

Seq::Seq(istream &is, BIO::FileFormat ff) : _id(0)
{
	_readFromFile(is, ff);
}

Seq::Seq(Seq &from, Seq::size_type start, Seq::size_type num, BIO::SeqFlags flags) : _title(from.getTitle()), _id(from.getID())
{
	_copyFrom(from, start, num, flags);
}

Seq::Seq(Seq &from, Vec<char> &alignment, char me) : _title(from.getTitle()), _id(from.getID())
{
	_alignFrom(from, alignment, me);
}

Seq::size_type Seq::getLength() const
{
	size_type l = _data.size();

	/* Do not count the first dummy character */
	if (l > 0)
		l--;

	return l;
}

string Seq::getTitle() const
{
	return _title;
}

unsigned int Seq::getID() const
{
	return _id;
}

char Seq::getLetter(Seq::size_type index) const
{
	return _data[index];
}

Seq::iterator Seq::getBegin()
{
	return _data.begin()+1; //skip the dummy character
}

Seq::iterator Seq::getIterator(Seq::size_type index)
{
	return _data.begin() + index;
}

Seq::iterator Seq::getEnd()
{
	return _data.end();
}
Seq::const_iterator Seq::getBegin() const
{
	return _data.begin()+1; //skip the dummy character
}

Seq::const_iterator Seq::getIterator(Seq::size_type index) const
{
	return _data.begin() + index;
}

Seq::const_iterator Seq::getEnd() const
{
	return _data.end();
}

Seq::size_type Seq::countLetters() const
{
	size_type sz = 0;
	const_iterator end_iter = _data.end();
	for (const_iterator i_iter = _data.begin()+1; i_iter < end_iter; i_iter++)
		sz += (*i_iter != '-');

	return sz;
}

void Seq::setTitle(string s)
{
	_title = s;
}

void Seq::setID(unsigned int id)
{
	_id = id;
}

void Seq::changeLetter(char letter, Seq::size_type index)
{
	_data[index] = letter;
}

void Seq::writeASCII(ostream &os)
{
	const_iterator end_iter = _data.end();
	for (const_iterator i_iter = _data.begin()+1; i_iter < end_iter; i_iter++)
	{
		/* Note: Isn't it somewhat inefficient, to print char-by-char? */
		os << *i_iter;
	}
}

void Seq::writeToFile(ostream &os, BIO::FileFormat ff, unsigned int width, bool useID)
{
	/* Check that the output stream is fine */
	assert(os.good());

	/* Fasta sequence format */
	if (ff == BIO::FF_FASTA)
	{
		/* Header */
		if (useID)
			os << ">S" << _id << endl;
		else
			os << ">" << _title << endl;

		unsigned int remain = width;
		const_iterator end_iter = _data.end();

		/* Dump sequence, and every "width" columns enter a newline */
		for (const_iterator i_iter = _data.begin()+1; i_iter < end_iter; i_iter++)
		{
			os << *i_iter;
			if (--remain == 0)
			{
				remain = width;
				os << endl;
			}
		}

		/* Enter a final newline for the last line */
		if (remain != width)
			os << endl;
	}
	else
	{
		throw BIO::E_InvalidFormatEx();
		//TODO: Is FF_XFASTA possible for one sequence?
	}
}

void Seq::clear()
{
	_id = 0;
	_title = "";
	_data.resize(0);
}

void Seq::readFromFile(string fname, BIO::FileFormat ff)
{
	_readFromFile(fname, ff);
}

void Seq::readFromFile(istream &is, BIO::FileFormat ff)
{
	_readFromFile(is, ff);
}

void Seq::copyFrom(Seq &from, size_type start, size_type num)
{
	_title = from.getTitle();
	_id = from.getID();
	_copyFrom(from, start, num);
}

void Seq::alignFrom(Seq &from, Vec<char> &alignment, char me)
{
	_title = from.getTitle();
	_id = from.getID();
	_alignFrom(from, alignment, me);
}

char &Seq::operator[](size_type index)
{
	return _data[index];
}

const char &Seq::operator[](size_type index) const
{
	return _data[index];
}

ostream &operator<<(ostream &os, Seq &s)
{
	//s.writeASCII(os);
	s.writeToFile(os);
	return os;
}

void Seq::_readFromFile(string fname, BIO::FileFormat ff)
{
	char buffer[BIO::IO_BUF_SIZE];
	ifstream is;
	
	/* Associate buffer with stream */
	is.rdbuf()->pubsetbuf(buffer, BIO::IO_BUF_SIZE);

	/* Open the file */
	if (!(is.rdbuf()->open(fname.c_str(), ios_base::in)))
		throw BIO::E_OpenFailedEx();

	_readFromFile(is, ff);
	
	/* Close the file */
	if (!(is.rdbuf()->close()))
		throw BIO::E_CloseFailedEx();
}

void Seq::_readFromFile(istream &is, BIO::FileFormat ff)
{
	/* Check that the input stream is fine */
	assert(is.good());

	char c;
	
	_title = "";
	_data.resize(1);
	_data[0] = BIO::SPECIAL;
	/* Fasta sequence format */
	if (ff == BIO::FF_FASTA)
	{
		/* Locate the first '>' */
		do
			is.get(c);
		while ((c != '>') && (is.good()));

		if (c != '>')
			throw BIO::E_MissingFastaStartEx();
		
		/* Continue by reading the header */
		for (is.get(c); (c != '\n') && (is.good()); _title += c, is.get(c));

		if (is.fail())
			throw BIO::E_InvalidFastaHeaderEx();

		/* Finally read the sequence, until EOF or another '>' appears */
		while (is.get(c))
		{
			if (c == '>')
			{
				is.putback('>');
				break;
			}
			if (isspace(c))
				continue;
			if ((c >= 'a') && (c <= 'z'))
				c += 'A' - 'a'; //TODO: There's a quicker version: just XOR a specific bit (but: is that portable?)
			if (((c < 'A') || (c > 'Z')) && (c != '-'))
				throw BIO::E_InvalidCharacterEx();

			_data.push_back(c);
		}

		/* Did we read anything at all? */
		if (getLength() == 0)
			throw BIO::E_ReadFailedEx();
	}
	else
	{
		throw BIO::E_InvalidFormatEx();
		//TODO: Is FF_XFASTA possible for one sequence?
	}
}

void Seq::_copyFrom(Seq &from, size_type start, size_type num, BIO::SeqFlags flags)
{
	/* Check to see if the numbers agree */
	assert(start + num - 1 <= from.getLength());

	_data.resize(1);
	_data[0] = BIO::SPECIAL;

	/* Copy from the other alignment */
	_data.insert(_data.end(), from.getBegin() + start - 1, from.getBegin() + start + num - 1);

	/* Reverse if necessary */
	if(flags & BIO::FLAG_REVERSE) {
		reverse(_data.begin() + 1, _data.end());
	}

	/* Complement if necessary */
	if(flags & BIO::FLAG_COMPLEMENT) {
		// XXX - Probably a more efficient way of doing this...
		for(iterator curr = getBegin(), end =  getEnd(); curr != end; curr++) {
			switch(*curr) {
				case 'A':
					*curr = 'T';
					break;
				case 'T':
					*curr = 'A';
					break;
				case 'C':
					*curr = 'G';
					break;
				case 'G':
					*curr = 'C';
					break;
			}
		}
	}
}

void Seq::rotate(size_type shift)
{
	std::rotate(_data.begin() + 1, _data.end() - shift, _data.end());
}

void Seq::_alignFrom(Seq &from, Vec<char> &alignment, char me)
{
	_data.resize(1);
	_data[0] = BIO::SPECIAL;

	const_iterator s_iter = from.getBegin();
	for (Vec<char>::const_iterator a_iter = alignment.begin(), end_iter = alignment.end(); a_iter < end_iter; a_iter++)
	{
		if ((*a_iter == me) || (*a_iter == BIO::ALIGN_BOTH))
			_data.push_back(*(s_iter++));
		else
			_data.push_back('-');
	}
}

