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

#ifndef CONSTANTS_H
#define CONSTANTS_H

#include <string>

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                               *
 * Constants and special types used within our modules.          *
 *                                                               *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

/*
* Notes:
*
* For safety, I have included everything within a "BIO" namespace.
* This means either say i.e. "BIO::FF_MFA" or "using namespace BIO"
*                                             --George@2004-04-27
*/

namespace BIO
{
	/* File formats */
	enum FileFormat
	{
		FF_AUTO,    //auto-detection; not implemented yet
		FF_FASTA,   //FASTA, Multi-FASTA or Multi-FASTA Alignment (MFA) format
		FF_XFASTA,  //The eXtended version of the above formats
		FF_TEXT,    //Text format as done by mpretty
		FF_VISTA    //Binary format understood by VISTA (nucleotides only!)
	};

	/* Exceptions for errors */
	class E_BioEx
	{
	 public:
		E_BioEx(std::string message) : _message(message) {}
		std::string getMessage() const { return _message; }

	 private:
		std::string _message;
	};

	class E_MissingFastaStartEx : public E_BioEx
	{
	 public:
		E_MissingFastaStartEx() : E_BioEx("Missing Fasta start") {}
	};
	class E_InvalidFastaHeaderEx : public E_BioEx
	{
	 public:
		E_InvalidFastaHeaderEx() : E_BioEx("Invalid Fasta header") {}		
	};
	class E_InvalidCharacterEx : public E_BioEx
	{
	 public:
		E_InvalidCharacterEx() : E_BioEx("Invalid sequence character exception (recognized characters are a-z,A-Z,-)") {}
	};
	class E_ReadFailedEx : public E_BioEx
	{
	 public:
		E_ReadFailedEx() : E_BioEx("General read failure exception") {}
	};
	class E_InvalidFormatEx : public E_BioEx
	{
	 public:
		E_InvalidFormatEx() : E_BioEx("Invalid format exception") {}
	};
	class E_OpenFailedEx : public E_BioEx
	{
	 public:
		E_OpenFailedEx() : E_BioEx("Error opening file") {}
	};
	class E_CloseFailedEx : public E_BioEx
	{
	 public:
		E_CloseFailedEx() : E_BioEx("Error closing file") {}
	};
	class E_MissingSubstMatrixEx : public E_BioEx
	{
	 public:
		E_MissingSubstMatrixEx() : E_BioEx("Missing substitution matrix in scoring parameters") {}
	};
	class E_SPFileParseErrorEx : public E_BioEx
	{
	public:
		E_SPFileParseErrorEx() : E_BioEx("Error parsing scoring parameters file") {}
		E_SPFileParseErrorEx(std::string message) : E_BioEx("Error while parsing scoring parameters file: " + message) {}
	};

	/* The sequence's first (dummy) character */
	const char SPECIAL = '#';

	/* The characters for alignment strings */
	const char ALIGN_X = 'X';
	const char ALIGN_Y = 'Y';
	const char ALIGN_BOTH = 'B';

	/* The number of letters in the nucleotide alphabet */
	const unsigned int NUM_NUCLEOTIDES = 4;

	/* The number of letters in the alphabet (including gaps; this is just NUM_NUCLEOTIDES + one extra char '-' = 5) */ 
	const unsigned int NUM_ALPHABET = 5;

	/* What does a gap look like? */
	const char GAP_CHAR = '-';

	/* Special constant for 'N' (any nucleotide) */
	const char ANY_CHAR = 'N';

	/* Default buffer size (in bytes) for file i/o */
	const std::streamsize IO_BUF_SIZE = 1024;

	const float SMALL_FLOAT = 0.0000001;

	/* Flags passed to Seq constructor for creating copies of sequences */
	enum SeqFlags {
		 FLAG_NONE       = 0 // Dummy flag (default)
		,FLAG_REVERSE    = 1 // Reverse the original
		,FLAG_COMPLEMENT = 2 // Complement the original (tr/ACGTN-/TGCAN-/)
	};

	/* Operators to allow binary | and & on SeqFlags */
	inline SeqFlags operator|(const SeqFlags &__a, const SeqFlags &__b)
	{
		return SeqFlags(static_cast<int>(__a) | static_cast<int>(__b));
	}

	inline SeqFlags operator&(const SeqFlags &__a, const SeqFlags &__b)
	{
		return SeqFlags(static_cast<int>(__a) & static_cast<int>(__b));
	}
}



#endif
