*.dmp files are bcp-like dump from GenBank taxonomy database.

General information.
Field terminator is "\t|\t"
Row terminator is "\t|\n"

nodes.dmp file consists of taxonomy nodes. The description for each node includes the following
fields:
	tax_id					-- node id in GenBank taxonomy database
 	parent tax_id				-- parent node id in GenBank taxonomy database
 	rank					-- rank of this node (superkingdom, kingdom, ...) 
 	embl code				-- locus-name prefix; not unique
 	division id				-- see division.dmp file
 	inherited div flag  (1 or 0)		-- 1 if node inherits division from parent
 	genetic code id				-- see gencode.dmp file
 	inherited GC  flag  (1 or 0)		-- 1 if node inherits genetic code from parent
 	mitochondrial genetic code id		-- see gencode.dmp file
 	inherited MGC flag  (1 or 0)		-- 1 if node inherits mitochondrial gencode from parent
 	GenBank hidden flag (1 or 0)            -- 1 if name is suppressed in GenBank entry lineage
 	hidden subtree root flag (1 or 0)       -- 1 if this subtree has no sequence data yet
 	comments				-- free-text comments and citations

Taxonomy names file (names.dmp):
	tax_id					-- the id of node associated with this name
	name_txt				-- name itself
	unique name				-- the unique variant of this name if name not unique
	name class				-- (synonym, common name, ...)

Divisions file (division.dmp):
	division id				-- taxonomy database division id
	division cde				-- GenBank division code (three characters)
	division name				-- e.g. BCT, PLN, VRT, MAM, PRI...
	comments

Genetic codes file:
	genetic code id				-- GenBank genetic code id
	abbreviation				-- genetic code name abbreviation
	name					-- genetic code name
	cde					-- translation table for this genetic code
	starts					-- start codons for this genetic code

Deleted nodes file (delnodes.dmp):
	tax_id					-- deleted node id

Merged nodes file (merged.dmp):
	old_tax_id                              -- id of nodes which has been merged
	new_tax_id                              -- id of nodes which is result of merging

Citations file (citations.dmp):
	cit_id					-- the unique id of citation
	cit_key					-- citation key
	pubmed_id				-- unique id in PubMed database (0 if not in PubMed)
	medline_id				-- unique id in MedLine database (0 if not in MedLine)
	url					-- URL associated with citation
	text					-- any text (usually article name and authors).
						-- The following characters are escaped in this text by a backslash:
						-- newline (appear as "\n"),
						-- tab character ("\t"),
						-- double quotes ('\"'),
						-- backslash character ("\\").
	taxid_list				-- list of node ids separated by a single space
