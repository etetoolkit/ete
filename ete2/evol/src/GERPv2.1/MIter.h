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

#ifndef MITER_H
#define MITER_H

/*
 * Multiple Sequence Iterator
 */

#include "Vec.h"
#include "Seq.h"

using namespace std;

class MIter
{
	friend class Mseq;

	public:
	
	typedef Vec<Seq::iterator>::size_type size_type;
	typedef Vec<Seq::iterator>::iterator iterator;
	typedef Vec<Seq::iterator>::const_iterator const_iterator;

	MIter() { _data.resize(0); }

	iterator getBegin();
	iterator getIterator(size_type index);
	iterator getEnd();
	size_type getSize();
	bool hasLetters();
	char getConsensusChar();

	void copyChars(MIter &mi);

	bool operator<(const MIter &mi);
	bool operator>(const MIter &mi);
	bool operator<=(const MIter &mi);
	bool operator>=(const MIter &mi);
	bool operator==(const MIter &mi);
	bool operator!=(const MIter &mi);
	Seq::iterator &operator[](size_type index);
	/* ___Prefix only!___ You were warned! */
	MIter &operator++();
	MIter &operator--();
	MIter &operator+(Seq::size_type inc);
	MIter &operator-(Seq::size_type dec);
	
	private:
	
	Vec<Seq::iterator> _data;
	
};
#endif
