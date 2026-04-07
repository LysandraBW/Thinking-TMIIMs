import sqlite3

conn = sqlite3.connect("COL.db")
cursor = conn.cursor()

conn.execute('CREATE INDEX IF NOT EXISTS IndexID ON NameUsage ("col:ID")')

conn.execute('CREATE INDEX IF NOT EXISTS IndexRank ON NameUsage ("col:rank")')

conn.execute('CREATE INDEX IF NOT EXISTS IndexGenusLowerCase ON NameUsage (LOWER("col:genus"))')

conn.execute('CREATE INDEX IF NOT EXISTS IndexScientificNameLowerCase ON NameUsage (LOWER("col:scientificName"))')

conn.execute('CREATE INDEX IF NOT EXISTS IndexGenericNameLowerCase ON NameUsage (LOWER("col:genericName"))')

conn.execute('CREATE INDEX IF NOT EXISTS IndexGenericNameLowerCaseFirstCharacter ON NameUsage (SUBSTR(LOWER("col:genericName"), 1, 1))')

conn.execute('CREATE INDEX IF NOT EXISTS IndexSpecificEpithetLowerCase ON NameUsage (LOWER("col:specificEpithet"))')

conn.execute('CREATE INDEX IF NOT EXISTS IndexNameLowerCase ON VernacularName (LOWER("col:name"))')

conn.execute('CREATE INDEX IF NOT EXISTS IndexTaxonID ON VernacularName ("col:taxonID")')

conn.execute('CREATE INDEX IF NOT EXISTS IndexLanguage ON VernacularName ("col:language")')

conn.execute('CREATE INDEX IF NOT EXISTS IndexLanguageEnglish ON VernacularName ("col:language") WHERE "col:language" = \'eng\'')

conn.execute('CREATE INDEX IF NOT EXISTS IndexLanguageTaxonID ON VernacularName ("col:language", "col:taxonID")')

conn.execute('''
    CREATE INDEX IF NOT EXISTS NameUsageVernacularNameJoinKey
    ON NameUsage("col:ID", "col:taxonID");
''')

conn.execute('''
    CREATE INDEX IF NOT EXISTS IndexLanguageEnglishJoin
    ON VernacularName("col:taxonID")
    WHERE "col:language" = 'eng';
''')

cursor.executescript('''
    CREATE TABLE IF NOT EXISTS MappedName AS
    SELECT n."col:ID" AS ID,
           n."col:scientificName" AS ScientificName,
           v."col:name" AS VernacularName,
           n."col:kingdom" AS Kingdom,
           n."col:phylum" AS Phylum,
           n."col:subphylum" AS SubPhylum,
            n."col:class" AS Class,
            n."col:subclass" AS SubClass,
            n."col:order" AS TaxonOrder,
            n."col:suborder" AS SubOrder,
            n."col:superfamily" AS SuperFamily,
            n."col:family" AS Family,
            n."col:subfamily" AS SubFamily,
            n."col:genus" AS Genus,
            n."col:subgenus" AS SubGenus,
            n."col:genericName" AS GenericName,
            n."col:specificEpithet" AS SpecificEpithet,
            n."col:infraspecificEpithet" AS IntraspecificEpithet
    FROM NameUsage n
    JOIN VernacularName v ON n."col:ID" = v."col:taxonID"
    WHERE v."col:language" = 'eng';

    CREATE INDEX IF NOT EXISTS IndexID ON MappedName(LOWER("ID"));
    CREATE INDEX IF NOT EXISTS IndexScientificName ON MappedName(LOWER("ScientificName"));
    CREATE INDEX IF NOT EXISTS IndexVernacularName ON MappedName(LOWER("VernacularName"));
    CREATE INDEX IF NOT EXISTS IndexGenericName1 ON MappedName (SUBSTR(LOWER("GenericName"), 1, 1));
    CREATE INDEX IF NOT EXISTS IndexKingdom ON MappedName(LOWER("Kingdom"));
    CREATE INDEX IF NOT EXISTS IndexPhylum ON MappedName(LOWER("Phylum"));
    CREATE INDEX IF NOT EXISTS IndexSubPhylum ON MappedName(LOWER("SubPhylum"));
    CREATE INDEX IF NOT EXISTS IndexClass ON MappedName(LOWER("Class"));
    CREATE INDEX IF NOT EXISTS IndexSubClass ON MappedName(LOWER("SubClass"));
    CREATE INDEX IF NOT EXISTS IndexOrder ON MappedName(LOWER("TaxonOrder"));
    CREATE INDEX IF NOT EXISTS IndexSubOrder ON MappedName(LOWER("SubOrder"));
    CREATE INDEX IF NOT EXISTS IndexSuperFamily ON MappedName(LOWER("SuperFamily"));
    CREATE INDEX IF NOT EXISTS IndexFamily ON MappedName(LOWER("Family"));
    CREATE INDEX IF NOT EXISTS IndexSubFamily ON MappedName(LOWER("SubFamily"));
    CREATE INDEX IF NOT EXISTS IndexGenus ON MappedName(LOWER("Genus"));
    CREATE INDEX IF NOT EXISTS IndexSubGenus ON MappedName(LOWER("SubGenus"));
    CREATE INDEX IF NOT EXISTS IndexGenericNames ON MappedName(LOWER("GenericName"));
    CREATE INDEX IF NOT EXISTS IndexSpecificEpithet ON MappedName(LOWER("SpecificEpithet"));
    CREATE INDEX IF NOT EXISTS IndexIntraspecificEpithet ON MappedName(LOWER("IntraspecificEpithet"));
''')

cols = [
    ["Kingdom","col:kingdom"],
    ["Phylum","col:phylum"],
    ["Subphylum","col:subphylum"],
    ["Class","col:class"],
    ["Subclass","col:subclass"],
    ["Order","col:order"],
    ["Suborder","col:suborder"],
    ["Superfamily","col:superfamily"],
    ["Family","col:family"],
    ["Subfamily","col:subfamily"],
    ["Genus","col:genus"],
    ["Subgenus","col:subgenus"],
    ["GenericName","col:genericName"],
    ["SpecificEpithet","col:specificEpithet"],
    ["IntraspecificEpithet","col:infraspecificEpithet"],
    ["Species","col:species"],
    ["ScientificName","col:scientificName"]
]

for col in cols:
    conn.execute(f'''CREATE INDEX IF NOT EXISTS Index{col[0]}LowerCase ON NameUsage (LOWER("{col[1]}"))''')

cursor.close()
conn.commit()
conn.close()