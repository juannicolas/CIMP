#!/usr/bin/perl
use CGI qw(:standard);

require "/home/weoms/proc/globals/connDB.pl";


$|=1;
$cgi=new CGI;
print "Content-type: text/html\n\n";
my $dbh=connACITPdb();
if( $cgi->param()){
	getParams();
	search();
}
else {
	print qq{<?xml version="1.0" encoding="utf-8"?><Results><success>false</success><error><msg>Error: No data was sent to server</msg></error></Results>};
}
$dbh->disconnect;
exit 0;


sub search {
	my $err = 0;
	$st=qq{SELECT initId,teamId,description,dependNotes,owner FROM initTrackingFormtbl $whereClause};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><success>false</success><error><msg>Error: Cannot search for initiatives</msg></error></Results>}; return 0;}
	my $xml =qq{<?xml version="1.0" encoding="utf-8"?>
<CriticalItems>
	<success>true</success>
	};
	while(my(@result)=$sth->fetchrow_array) {
		$st=qq{SELECT name FROM teamstbl WHERE id = '$result[1]'};
		$sth2=$dbh->prepare($st);
		$sth2->execute();
		my $teamName=$sth2->fetchrow_array;
		$st=qq{ select fullName from userstbl where username='$result[4]'};
		$sth2=$dbh->prepare($st);
		$sth2->execute();
		my $ownerFullName=$sth2->fetchrow_array;
		$sth2->finish;
		$xml .= qq{<criticalItem>
		<id>$result[0]</id>
		<team><![CDATA[$result[1]. $teamName]]></team>
		<description><![CDATA[$result[2]]]></description>
		<dependNotes><![CDATA[$result[3]]]></dependNotes>
		<owner>$ownerFullName</owner>
	</criticalItem>
	};
	}
	$xml .= qq{</CriticalItems>};
	print $xml;
}




sub getParams {
	$teamId = $cgi->param('team');
	$owner = $cgi->param('owner');
	$whereClause = qq{WHERE dependIds <> ''};
	if($teamId > 0) {$whereClause .= qq{ AND teamId = '$teamId'};}
	if($owner ne "") {$whereClause .= qq{ AND owner = '$owner'};}
}


