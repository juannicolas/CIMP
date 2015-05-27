#!/usr/bin/perl

require "/home/weoms/proc/globals/connDB.pl";

$xmlDir = "/home/weoms/www/apps/ACITP/files";

my $dbh=connACITPdb();
#############Create teams.xml file
$xml = qq{<?xml version="1.0" encoding="utf-8"?>
<Teams>};
$st=qq{ select * from teamstbl};
$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
$sth->execute() or print "could not execute\n$!";
while(my(@result)=$sth->fetchrow_array){ 	
$xml .= qq{
	<team>
		<id>$result[0]</id>
		<name><![CDATA[#$result[0].  $result[1]]]></name>
		<description><![CDATA[$result[2]]]></description>
	</team>};
} $sth->finish;
$xml .= qq{
</Teams>};

open(TEAMS,">$xmlDir/teams.xml");
print TEAMS $xml;
close(TEAMS);

###############Create itemsCat.xml file
$xml = qq{<?xml version="1.0" encoding="utf-8"?>
<ItemCategories>};
$st=qq{ select * from categorytbl};
$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
$sth->execute() or print "could not execute\n$!";
while(my(@result)=$sth->fetchrow_array){ 	
$xml .= qq{
	<category>
		<id>$result[0]</id>
		<name>$result[1]</name>
	</category>};
} $sth->finish;
$xml .= qq{
</ItemCategories>};

open(CAT,">$xmlDir/itemsCat.xml");
print CAT $xml;
close(CAT);

###############Create users.xml file
$xml = qq{<?xml version="1.0" encoding="utf-8"?>
<Users>};
$st=qq{ select * from userstbl order by fullName};
$sth=$dbh->prepare($st) or print "Could not prepare on login: $!\n";
$sth->execute() or print "could not execute\n$!";
while(my(@result)=$sth->fetchrow_array){ 	
$xml .= qq{
	<user>
		<id>$result[0]</id>
		<username>$result[1]</username>
		<name>$result[3]</name>
	</user>};
} $sth->finish;
$xml .= qq{
</Users>};

open(USR,">$xmlDir/users.xml");
print USR $xml;
close(USR);

$dbh->disconnect;

