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

#include "Vec.h"
#include "Seq.h"
#include "Mseq.h"
#include "MIter.h"
#include "Constants.h"

using namespace std;

MIter::iterator MIter::getBegin()
{
	return _data.begin();
}

MIter::iterator MIter::getIterator(size_type index)
{
	return _data.begin() + index;
}

MIter::iterator MIter::getEnd()
{
	return _data.end();
}

MIter::size_type MIter::getSize()
{
	return _data.size();
}

bool MIter::hasLetters()
{
	iterator e_iter = getEnd();
	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
	{
		if (**i_iter != '-')
			return true;
	}
	return false;
}

char MIter::getConsensusChar()
{
	//This is thread unsafe but it will be faster
	if (_data.size() == 1)
	{
		return **getBegin();
	}
	static Mseq::size_type tbl[256];
	
	//Only the four letters are initialized to zero (Ouch!)
	tbl[(Mseq::size_type)(unsigned char)'A'] =
		tbl[(Mseq::size_type)(unsigned char)'C'] =
		tbl[(Mseq::size_type)(unsigned char)'T'] =
		tbl[(Mseq::size_type)(unsigned char)'G'] =
		tbl[(Mseq::size_type)(unsigned char)'N'] = 0;

	iterator e_iter = getEnd();
	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
		tbl[(Mseq::size_type)(unsigned char)(**i_iter)]++;

	char maxLetter = 'A';
	Mseq::size_type maxFreq = tbl[(Mseq::size_type)(unsigned char)'A'];

	if (maxFreq < tbl[(Mseq::size_type)(unsigned char)'T'])
	{
		maxLetter = 'T';
		maxFreq = tbl[(Mseq::size_type)(unsigned char)'T'];
	}
	if (maxFreq < tbl[(Mseq::size_type)(unsigned char)'C'])
	{
		maxLetter = 'C';
		maxFreq = tbl[(Mseq::size_type)(unsigned char)'C'];
	}
	if (maxFreq < tbl[(Mseq::size_type)(unsigned char)'G'])
		maxLetter = 'G';

	if ((maxLetter == 'A') && (maxFreq == 0)) //If we encountered only 'N's and '-'s
		return BIO::ANY_CHAR;
	else
		return maxLetter;
}

void MIter::copyChars(MIter &mi)
{
	iterator e_iter = getEnd(), f_iter = mi.getBegin();
	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++, f_iter++)
		**i_iter = **f_iter;
}

bool MIter::operator<(const MIter &mi)
{
	return _data[0] < mi._data[0];
}

bool MIter::operator>(const MIter &mi)
{
	return _data[0] > mi._data[0];
}

bool MIter::operator<=(const MIter &mi)
{
	return _data[0] <= mi._data[0];
}

bool MIter::operator>=(const MIter &mi)
{
	return _data[0] >= mi._data[0];
}

bool MIter::operator==(const MIter &mi)
{
	return _data[0] == mi._data[0];
}

bool MIter::operator!=(const MIter &mi)
{
	return _data[0] != mi._data[0];
}

Seq::iterator &MIter::operator[](size_type index)
{
	return _data[index];
}

MIter &MIter::operator++()
{
	iterator e_iter = getEnd();
	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
		++(*i_iter);

	return *this;
}

MIter &MIter::operator--()
{
	iterator e_iter = getEnd();
	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
		--(*i_iter);

	return *this;
}

MIter &MIter::operator+(Seq::size_type inc)
{
	iterator e_iter = getEnd();
	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
		(*i_iter) += inc;
	
	return *this;
}

MIter &MIter::operator-(Seq::size_type dec)
{
	iterator e_iter = getEnd();
	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
		(*i_iter) -= dec;
	
	return *this;
}
