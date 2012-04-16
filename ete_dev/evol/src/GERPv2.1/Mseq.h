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

#ifndef MSEQ_H
#define MSEQ_H

#include "Vec.h"
#include "Constants.h"
#include "Seq.h"
#include "MIter.h"
using namespace std;

class Mseq
{
	public:

	/* Types */
	/* ===== */
	
	typedef Vec<Seq>::size_type size_type;
	typedef Vec<Seq>::iterator iterator;
	typedef Vec<Seq>::const_iterator const_iterator;

	/* Constructors */
	/* ============ */

	/* Empty Constructor */
	Mseq() { _data.resize(0); }

	/* Multiple Sequence from filename */
	Mseq(string fname, BIO::FileFormat ff = BIO::FF_FASTA);

	/* Multiple Sequence from input stream */
	Mseq(istream &is, BIO::FileFormat ff = BIO::FF_FASTA);

	/* Multiple Sequence copied from another Mseq */
	Mseq(Mseq &from, Seq::size_type start, Seq::size_type num);

	/* Multiple (actually, Single!) Sequence copied from a Seq */
	Mseq(Seq &from, Seq::size_type start, Seq::size_type num);

	/* Multiple Sequence created from alignment (partial, like in Seq.h) */
	Mseq(Mseq &from, Vec<char> &alignment, char me);

	/* Multiple Sequence created from alignment (complete) */
	Mseq(Mseq &fromX, Mseq &fromY, Vec<char> &alignment);

	/* Multiple Sequence created from projection */
	Mseq(Mseq &from, Vec<Mseq::size_type> &indices);

	/* Multiple Sequence created from removing columns where a certain species (idx) has gaps */
	Mseq(Mseq &from, Mseq::size_type idx);

	/* Methods */
	/* ======= */
	
	size_type getSize() const;
	Seq::size_type getLength() const;
	Seq &getSequence(size_type index);
	char getLetter(size_type seqindex, Seq::size_type index) const; //Retrieve [index]-th letter from the [seqindex]-th sequence
	iterator getBegin();
	iterator getIterator(size_type index);
	iterator getEnd();
	const_iterator getBegin() const;
	const_iterator getIterator(size_type index) const;
	const_iterator getEnd() const;
	void getMIBegin(MIter &mi);
	void getMIBegin(MIter &mi, Vec<Mseq::size_type> &indices);
	void getMIter(MIter &mi, Seq::size_type index);
	void getMIter(MIter &mi, Seq::size_type index, Vec<Mseq::size_type> &indices);
	void getMIEnd(MIter &mi);
	void getMIEnd(MIter &mi, Vec<Mseq::size_type> &indices);

	void changeLetter(char letter, size_type seqindex, Seq::size_type index);
	void writeToFile(ostream &os, BIO::FileFormat ff = BIO::FF_FASTA, unsigned int width = 78, bool useID = false);
	//   The score() method computes a sum-of-pairs score for the Mseq.
	//   The substitution matrix is a 256x256 matrix, incorporating the gap extension
	//   penalties in the [nucl]['-'] entries. gap_event is the gap open + gap close penalty,
	//   gterminal is the terminal gap penalty with default to 0, out is the stream where
	//   the score and some other statistics will be printed, and gap_single is the gap
	//   single penalty.
	float score(const Vec< Vec<float> > &subst_matrix, float gap_event, float gterminal = 0, ostream &out = cout, float gap_single = 0);

	// Create an alignment string like that taken by alignFrom (e.g. "XXXBBYYYBBYYXX")
	// given the indices of two sequences in the current Mseq
	Vec<char> getAlignment(Seq::size_type X_index, Seq::size_type Y_index) const;

	void erase(Seq::size_type pos);

	// Constructor-like methods
	void clear();
	void readFromFile(string fname, BIO::FileFormat ff = BIO::FF_FASTA);
	void readFromFile(istream &is, BIO::FileFormat ff = BIO::FF_FASTA);
	bool readSeqFromFile(istream &is, BIO::FileFormat ff = BIO::FF_FASTA);
	void copyFrom(Mseq &from, Seq::size_type start, Seq::size_type num);
	void copyFrom(Seq &from, Seq::size_type start, Seq::size_type num);
	void alignFrom(Mseq &from, Vec<char> &alignment, char me);
	void alignFrom(Mseq &fromX, Mseq &fromY, Vec<char> &alignment);
	void projectFrom(Mseq &from, Vec<Mseq::size_type> &indices);
	void projectSingle(Mseq &from, Mseq::size_type idx);

	//This "dusts" the sequence
	void dustMseq(unsigned int level = 28);
	
	/* Operators */
	/* ========= */

	Seq &operator[](size_type index);
	const Seq &operator[](size_type index) const;
	friend ostream &operator<<(ostream &os, Mseq &s);

	private:

	Vec<Seq> _data;
	void _readFromFile(string fname, BIO::FileFormat ff);
	void _readFromFile(istream &is, BIO::FileFormat ff);
	bool _readSeqFromFile(istream &is, BIO::FileFormat ff = BIO::FF_FASTA);
	void _copyFrom(Mseq &from, Seq::size_type start, Seq::size_type num);
	void _copyFrom(Seq &from, Seq::size_type start, Seq::size_type num);
	void _alignFrom(Mseq &from, Vec<char> &alignment, char me);
	void _alignFrom(Mseq &fromX, Mseq &fromY, Vec<char> &alignment);
	void _projectFrom(Mseq &from, Vec<Mseq::size_type> &indices);
	void _projectSingle(Mseq &from, Mseq::size_type idx);
	void _dustMseq(unsigned int level);
};

#endif
