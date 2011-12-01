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

/* =================
 * Multiple Sequence
 * =================
 *
 * See Mseq.h for more info
 *
 */

#include "Mseq.h"
#include "Vec.h"
#include "Seq.h"
#include "Constants.h"
#include "MIter.h"
#include <cassert>
#include <iostream>
#include <math.h>


using namespace std;

Mseq::Mseq(string fname, BIO::FileFormat ff)
{
	_readFromFile(fname, ff);
}

Mseq::Mseq(istream &is, BIO::FileFormat ff)
{
	_readFromFile(is, ff);
}

Mseq::Mseq(Mseq &from, Seq::size_type start, Seq::size_type num)
{
	_copyFrom(from, start, num);
}

Mseq::Mseq(Seq &from, Seq::size_type start, Seq::size_type num)
{
	_copyFrom(from, start, num);
}

Mseq::Mseq(Mseq &from, Vec<char> &alignment, char me)
{
	_alignFrom(from, alignment, me);
}

Mseq::Mseq(Mseq &fromX, Mseq &fromY, Vec<char> &alignment)
{
	_alignFrom(fromX, fromY, alignment);
}

Mseq::Mseq(Mseq &from, Vec<Mseq::size_type> &indices)
{
	_projectFrom(from, indices);
}

Mseq::Mseq(Mseq &from, Mseq::size_type idx)
{
	_projectSingle(from, idx);
}

Mseq::size_type Mseq::getSize() const
{
	return _data.size();
}

Seq::size_type Mseq::getLength() const
{
	assert(_data.size() > 0);
	return _data[0].getLength();
}

Seq &Mseq::getSequence(Mseq::size_type index)
{
	return _data[index];
}

char Mseq::getLetter(Mseq::size_type seqindex, Seq::size_type index) const
{
	return _data[seqindex][index];
}

Mseq::iterator Mseq::getBegin()
{
	return _data.begin();
}

Mseq::iterator Mseq::getIterator(Mseq::size_type index)
{
	return _data.begin() + index;
}

Mseq::iterator Mseq::getEnd()
{
	return _data.end();
}
Mseq::const_iterator Mseq::getBegin() const
{
	return _data.begin();
}

Mseq::const_iterator Mseq::getIterator(Mseq::size_type index) const
{
	return _data.begin() + index;
}

Mseq::const_iterator Mseq::getEnd() const
{
	return _data.end();
}

void Mseq::getMIBegin(MIter &mi)
{
	mi._data.resize(getSize());

	iterator e_iter = getEnd();
	MIter::iterator m_iter = mi.getBegin();

	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
		*(m_iter++) = i_iter->getBegin();
}

void Mseq::getMIBegin(MIter &mi, Vec<Mseq::size_type> &indices)
{
	mi._data.resize(indices.size());

	Vec<Mseq::size_type>::iterator e_iter = indices.end();
	MIter::iterator m_iter = mi.getBegin();

	for (Vec<Mseq::size_type>::iterator i_iter = indices.begin(); i_iter < e_iter; i_iter++)
		*(m_iter++) = _data[*i_iter].getBegin();
}

void Mseq::getMIter(MIter &mi, Seq::size_type index)
{
	mi._data.resize(getSize());

	iterator e_iter = getEnd();
	MIter::iterator m_iter = mi.getBegin();

	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
		*(m_iter++) = i_iter->getIterator(index);
}

void Mseq::getMIter(MIter &mi, Seq::size_type index, Vec<Mseq::size_type> &indices)
{
	mi._data.resize(indices.size());

	Vec<Mseq::size_type>::iterator e_iter = indices.end();
	MIter::iterator m_iter = mi.getBegin();

	for (Vec<Mseq::size_type>::iterator i_iter = indices.begin(); i_iter < e_iter; i_iter++)
		*(m_iter++) = _data[*i_iter].getIterator(index);
}

void Mseq::getMIEnd(MIter &mi)
{
	mi._data.resize(getSize());

	iterator e_iter = getEnd();
	MIter::iterator m_iter = mi.getBegin();

	for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
		*(m_iter++) = i_iter->getEnd();
}

void Mseq::getMIEnd(MIter &mi, Vec<Mseq::size_type> &indices)
{
	mi._data.resize(indices.size());

	Vec<Mseq::size_type>::iterator e_iter = indices.end();
	MIter::iterator m_iter = mi.getBegin();

	for (Vec<Mseq::size_type>::iterator i_iter = indices.begin(); i_iter < e_iter; i_iter++)
		*(m_iter++) = _data[*i_iter].getEnd();
}

void Mseq::changeLetter(char letter, Mseq::size_type seqindex, Seq::size_type index)
{
	_data[seqindex].changeLetter(letter, index);
}

void Mseq::writeToFile(ostream &os, BIO::FileFormat ff, unsigned int width, bool useID)
{
	/* Check that the output stream is fine */
	assert(os.good());

	if (ff == BIO::FF_FASTA)
	{
		iterator e_iter = getEnd();
		for (iterator i_iter = getBegin(); i_iter < e_iter; i_iter++)
			i_iter->writeToFile(os, ff, width, useID);
	}
	else if (ff == BIO::FF_TEXT)
	{
		//TODO this and other file formats
	}
}


float Mseq::score(const Vec< Vec<float> > &subst_matrix, float gap_event, float gterminal, ostream &o, float gs)
{
	unsigned int nseqs, length;

	assert( ( nseqs  = getSize() )   >= 2);
	assert( ( length = getLength() ) >= 2);

	float score = 0;
	unsigned int nmatches = 0, nmismatches = 0, ngaps = 0, ngo = 0, ngc = 0, ngs = 0;
	
	for (unsigned int x_idx = 0; x_idx < nseqs-1; ++x_idx) {
		for (unsigned int y_idx = x_idx+1; y_idx < nseqs; ++y_idx) {
			
			Vec< Mseq::size_type > indices(2);
			indices[ 0 ] = x_idx;
			indices[ 1 ] = y_idx;

			Mseq xy;
			xy.projectFrom(*this, indices );

			Seq &x = xy.getSequence( 0 );
			Seq &y = xy.getSequence( 1 );

			length = x.getLength();
			assert(length == y.getLength());

			// First compute the substitution scores (including gap extensions);
			
			char x_i, y_i;
			Seq::const_iterator x_iter, y_iter, e_iter;

			for (x_iter = x.getBegin(), y_iter = y.getBegin(), e_iter = x.getEnd(); x_iter < e_iter; ++x_iter, ++y_iter) {
				x_i = *x_iter;
				y_i = *y_iter;
				score += subst_matrix[ (int)x_i ][ (int)y_i ];

				if ( x_i == y_i ) ++nmatches;
				else if ( x_i == '-' || y_i == '-' ) ++ngaps;
				else ++nmismatches;
			}

			// Then, compute gap open, close, single scores

			for (unsigned int currseq_idx = 0; currseq_idx <= 1; ++currseq_idx) {
				Seq &currseq = currseq_idx ? y : x;

				unsigned int i = 1;

				while ( i <= length && currseq[ i ] == '-' ) ++i;
				assert( i <= length );

				if ( i > 1 ) {
					++ngc;
					
					if (fabsf(gterminal) >= BIO::SMALL_FLOAT) score += gterminal;
					else                               score += gap_event;
				}

				while ( i <= length ) {
					while ( i <= length && currseq[ i ] != '-' ) ++i;
					while ( i <= length && currseq[ i ] == '-' ) ++i;
					
					if ( i <= length ) {
						if ( currseq[ i - 2 ] != '-' ) { // single gap case
							++ngs;
							if (fabsf(gs) > BIO::SMALL_FLOAT) score += gs;
							else                       score += gap_event;
						}
						else {
							++ngo;
							++ngc;
							score += gap_event;
						}
					}
				}
				if ( currseq[ i - 1 ] == '-' ) {
					++ngo;
					
					if (fabsf(gterminal) >= BIO::SMALL_FLOAT) {
						score += gterminal;
					}
					else {
						score += gap_event;
					}
				}
			}
		}
	}
	o << "Score: " << score << endl;
	o << "Matches: " << nmatches << ";  mismatches: " << nmismatches << endl;
	o << "Gap open: " << ngo << ";  total gap positions: " << ngaps << ";  close: " << ngc << ";  single: " << ngs << endl;

	return score;
}

Vec<char> Mseq::getAlignment(Seq::size_type X_index, Seq::size_type Y_index) const
{
	Vec<char> alignment(getLength(), BIO::SPECIAL);

	assert( getSize() > X_index );
	assert( getSize() > Y_index );

	Seq X = (*this)[X_index];
	Seq Y = (*this)[Y_index];

	Seq::iterator X_iter = X.getBegin(),
	              Y_iter = Y.getBegin(),
	              X_end = X.getEnd(),
	              Y_end = Y.getEnd();

	size_t count_x = 0, count_y = 0, count_b = 0;

	for( Seq::size_type i=0, end=getLength() ;
	     i < end ;
	     ++i, ++X_iter, ++Y_iter)
	{
		char x = *X_iter;
		char y = *Y_iter;

		if(x == '-' && y == '-')
		{
			cerr << "WARNING: getAlignment() encountered simultaneous gaps.  This is probably not handled gracefully..." << endl;

			// Skip this entry in the alignment vector
			i--;
			end--;

			// Resize alignment vector
			alignment.pop_back();

			// Continue loop
			continue;
		}

		else if(x == '-')
		{
			// Insertion in Y
			alignment[i] = BIO::ALIGN_Y;
			count_y++;
		}

		else if(y == '-')
		{
			// Insertion in X
			alignment[i] = BIO::ALIGN_X;
			count_x++;
		}

		else
		{
			// Match
			alignment[i] = BIO::ALIGN_BOTH;
			count_x++;
			count_y++;
			count_b++;
		}
	}

	return alignment;
}

void Mseq::clear()
{
	_data.resize(0);
}

void Mseq::readFromFile(string fname, BIO::FileFormat ff)
{
	_readFromFile(fname, ff);
}

void Mseq::readFromFile(istream &is, BIO::FileFormat ff)
{
	_readFromFile(is, ff);
}

bool Mseq::readSeqFromFile(istream &is, BIO::FileFormat ff)
{
	return _readSeqFromFile(is, ff);
}

void Mseq::copyFrom(Mseq &from, Seq::size_type start, Seq::size_type num)
{
	_copyFrom(from, start, num);
}

void Mseq::copyFrom(Seq &from, Seq::size_type start, Seq::size_type num)
{
	_copyFrom(from, start, num);
}

void Mseq::alignFrom(Mseq &from, Vec<char> &alignment, char me)
{
	_alignFrom(from, alignment, me);
}

void Mseq::alignFrom(Mseq &fromX, Mseq &fromY, Vec<char> &alignment)
{
	_alignFrom(fromX, fromY, alignment);
}

void Mseq::projectFrom(Mseq &from, Vec<Mseq::size_type> &indices)
{
	_projectFrom(from, indices);
}

void Mseq::projectSingle(Mseq &from, Mseq::size_type idx)
{
	_projectSingle(from, idx);
}

/*
void Mseq::dustMseq(unsigned int level)
{
	_dustMseq(level);
}
*/

Seq &Mseq::operator[](size_type index)
{
	return _data[index];
}

const Seq &Mseq::operator[](size_type index) const
{
	return _data[index];
}

ostream &operator<<(ostream &os, Mseq &s)
{
	s.writeToFile(os);
	return os;
}

void Mseq::_readFromFile(string fname, BIO::FileFormat ff)
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

void Mseq::_readFromFile(istream &is, BIO::FileFormat ff)
{
	// TODO: Implement the rest of the file formats
	// Right now only FF_FASTA is supported
	clear();

	size_type n = 0;
	while (is.good() && (!is.eof()))
	{
		_data.resize(n+1);
		_data[n].readFromFile(is, ff);
		n++;
	}
}

bool Mseq::_readSeqFromFile(istream &is, BIO::FileFormat ff)
{
	clear();
	_data.resize(1);
	_data[0].readFromFile(is, ff);
	return (is.good() && !is.eof());
}

void Mseq::_copyFrom(Mseq &from, Seq::size_type start, Seq::size_type num)
{
	clear();
	_data.resize(from.getSize());

	iterator e_iter = from.getEnd(), i_iter, f_iter;

	for (f_iter = from.getBegin(), i_iter = getBegin(); f_iter < e_iter; ++i_iter, ++f_iter)
		i_iter->copyFrom(*f_iter, start, num);
}

void Mseq::_copyFrom(Seq &from, Seq::size_type start, Seq::size_type num)
{
	clear();
	_data.resize(1);
	_data.begin()->copyFrom(from, start, num);
}

void Mseq::_alignFrom(Mseq &from, Vec<char> &alignment, char me)
{
	clear();
	_data.resize(from.getSize());

	iterator e_iter = from.getEnd(), i_iter, f_iter;

	for (f_iter = from.getBegin(), i_iter = getBegin(); f_iter < e_iter; ++i_iter, ++f_iter)
		i_iter->alignFrom(*f_iter, alignment, me);
}

void Mseq::_alignFrom(Mseq &fromX, Mseq &fromY, Vec<char> &alignment)
{
	clear();
	_data.resize(fromX.getSize() + fromY.getSize());

	iterator e_iter = fromX.getEnd(), i_iter, f_iter;

	for (f_iter = fromX.getBegin(), i_iter = getBegin(); f_iter < e_iter; ++i_iter, ++f_iter)
		i_iter->alignFrom(*f_iter, alignment, BIO::ALIGN_X);
	
	e_iter = fromY.getEnd();
	for (f_iter = fromY.getBegin(); f_iter < e_iter; ++i_iter, ++f_iter)
		i_iter->alignFrom(*f_iter, alignment, BIO::ALIGN_Y);
}

void Mseq::_projectFrom(Mseq &from, Vec<Mseq::size_type> &indices)
{
	clear();

	assert( from.getSize() >= indices.size() );

	_data.resize( indices.size() );

	/* Create two MIters */
	MIter mi_iter, me_iter;

	Seq::size_type sz = 0;
	
	/* Move the MIter through the sequences and count the columns which have at least one letter */
	from.getMIEnd(me_iter, indices);
	for (from.getMIBegin(mi_iter, indices); mi_iter < me_iter; ++mi_iter)
		sz += (mi_iter.hasLetters());

	/* Initialize the new sequences accordingly */
	Vec<Mseq::size_type>::iterator e_iter = indices.end();
	iterator s_iter = getBegin();

	for (Vec<Mseq::size_type>::iterator i_iter = indices.begin(); i_iter < e_iter; i_iter++, s_iter++)
	{
		s_iter->_data.resize(sz+1);
		s_iter->_data[0] = BIO::SPECIAL;
		s_iter->_id = from._data[*i_iter]._id;
		s_iter->_title = from._data[*i_iter]._title;
	}

	/* Fill the new sequences */
	MIter this_iter;
	getMIBegin(this_iter);
	for (from.getMIBegin(mi_iter, indices); mi_iter < me_iter; ++mi_iter)
		if (mi_iter.hasLetters())
		{
			this_iter.copyChars(mi_iter);
			++this_iter;
		}
}

void Mseq::_projectSingle(Mseq &from, Mseq::size_type idx)
{
	clear();

	assert( from.getSize() > idx );

	_data.resize( from.getSize() );

	/* Count the columns which have a letter in the idx sequence */
	Seq::size_type sz = from[idx].countLetters();

	/* Initialize the new sequences accordingly */
	iterator s_iter = getBegin(), e_iter = from.getEnd();

	for (iterator i_iter = from.getBegin(); i_iter < e_iter; i_iter++, s_iter++)
	{
		s_iter->_data.resize(sz+1);
		s_iter->_data[0] = BIO::SPECIAL;
		s_iter->_id = i_iter->getID();
		s_iter->_title = i_iter->getTitle();
	}

	/* Create two MIters */
	MIter mi_iter, me_iter;
	from.getMIEnd(me_iter);

	/* Fill the new sequences */
	MIter this_iter;
	getMIBegin(this_iter);
	for (from.getMIBegin(mi_iter); mi_iter < me_iter; ++mi_iter)
		if ((*(mi_iter[idx])) != '-')
		{
			this_iter.copyChars(mi_iter);
			++this_iter;
		}
}

//utility for 
/*
namespace DUST_UTIL
{
	char maskN(char c)
	{
		return 'N';
	}
}

void Mseq::_dustMseq(unsigned int level)
{
	iterator end = getEnd();
	for (iterator iter = getBegin(); iter != end; ++iter)
	{
		//first convert each sequence into a fasta file structure that dust understands
		FastaSeq fastaSeq;
		fastaSeq.len = iter->getLength();
		fastaSeq.seq = new char[fastaSeq.len];
		copy(iter->getBegin(), iter->getEnd(), fastaSeq.seq);

		dust(&fastaSeq, level, &DUST_UTIL::maskN);
		
		copy(fastaSeq.seq, fastaSeq.seq + fastaSeq.len, iter->getBegin());
		delete fastaSeq.seq;

	}
	
}
*/
void Mseq::erase(Seq::size_type pos)
{
	for( iterator iter = getBegin(), end = getEnd() ; iter != end ; ++iter )
	{
		Seq &s = *iter;
		s._data.erase( s.getBegin() + pos - 1 );
	}
}
