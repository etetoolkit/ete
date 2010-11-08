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


#ifndef VEC_H
#define VEC_H

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                               *
 * Vec is a vector wrapper that does optional bounds checking    *
 *                                                               *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

/*
* Notes:
* -----
*
* Define VEC_ENABLED_CHECKS if you actually want to do bounds
* checking. Production (release) versions should undefine that
* (hopefully... :)                             --George@2004-04-26
*
*/

#include <vector>

template< typename T, typename Alloc = std::allocator<T> >
class Vec : public std::vector<T, Alloc>
{
	typedef std::vector<T, Alloc> _Parent;

	public:

	typedef typename _Parent::size_type size_type;

	Vec() : _Parent() {}
	Vec(size_type size) : _Parent(size) {}
	Vec(size_type size, const T &value) : _Parent(size, value) {}
	Vec(const Vec &from) : _Parent(from) {}

#ifdef VEC_ENABLE_CHECKS
	/* "Safe" version of "[]" operator */
	T &operator[](size_type index)
	{
		/* Let "at" do the bound checking ;-) */
		return at(index);
	}

	/* "Safe" version of const "[]" operator */
	const T &operator[] (size_type index) const
	{
		/* Let "at" do the bound checking */
		return at(index);
	}
#endif
};
#endif
