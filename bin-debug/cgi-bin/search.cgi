#!/usr/bin/perl
use CGI qw(:standard);

require "/home/weoms/proc/globals/connDB.pl";


$|=1;
$cgi=new CGI;
print "Content-type: text/html\n\n";
my $dbh=connACITPdb();
if( $cgi->param()){
	$action= $cgi->param('action');
	getParams();
	if($action eq "getAll") {search();}
	elsif($action eq "view"){view();}
}
else {
	print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: No data was sent to server</msg></error></Results>};
}
$dbh->disconnect;
exit 0;


sub search {
	my $err = 0;
	$st=qq{SELECT initId,teamId,description,owner FROM initTrackingFormtbl $whereClause};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot search for initiatives</msg></error></Results>}; return 0;}
	my $xml =qq{<?xml version="1.0" encoding="utf-8"?>
<Initiatives>
	<procResult><value>true</value><prevAction>$action</prevAction></procResult>
	};
	while(my(@result)=$sth->fetchrow_array) {
		$st=qq{SELECT name FROM teamstbl WHERE id = '$result[1]'};
		$sth2=$dbh->prepare($st);
		$sth2->execute();
		my $teamName=$sth2->fetchrow_array;
		$st=qq{ select fullName from userstbl where username='$result[3]'};
		$sth2=$dbh->prepare($st);
		$sth2->execute();
		my $ownerFullName=$sth2->fetchrow_array;
		$sth2->finish;
		$xml .= qq{<initiative>
		<id>$result[0]</id>
		<team><![CDATA[$result[1]. $teamName]]></team>
		<description><![CDATA[$result[2]]]></description>
		<owner>$ownerFullName</owner>
	</initiative>
	};
	}
	$xml .= qq{</Initiatives>};
	print $xml;
}

sub view {
	my $err = 0;
	#open(LOGF,">log.xml");
	$st=qq{SELECT * FROM initTrackingFormtbl $whereClause ORDER BY initId};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot search for initiative: $initId</msg></error></Results>}; return 0;}
	my $xml =qq{<?xml version="1.0" encoding="utf-8"?>
<Initiatives>
	<procResult><value>true</value><prevAction>$action</prevAction></procResult>
	};
	while(my(@result)=$sth->fetchrow_array) {
		$st=qq{ select * from userstbl where username='$user'};
		my $sth2=$dbh->prepare($st);
		$sth2->execute();
		my @userInfo =$sth2->fetchrow_array;
		if($result[2] eq $user || $userInfo[4] == 1) {$canModify = "true";}
		else {$canModify = "false";}
		my $teamIndex = $result[1] - 1;
		$result[4] =~ s/\G(\d{1,3})(?=(?:\d\d\d)+(?:\.|$))/$1,/g;
		$result[4] = '$' . $result[4];
		$result[6] =~ s/\G(\d{1,3})(?=(?:\d\d\d)+(?:\.|$))/$1,/g;
		$result[6] = '$' . $result[6];
		$xml .= qq{<initiative>
		<id>$result[0]</id>
		<team>$teamIndex</team>
		<description><![CDATA[$result[3]]]></description>
		<expense><![CDATA[$result[4]]]></expense>
		<expDesc><![CDATA[$result[13]]]></expDesc>
		<capital><![CDATA[$result[6]]]></capital>
		<capDesc><![CDATA[$result[14]]]></capDesc>
		<dependNotes><![CDATA[$result[9]]]></dependNotes>
		<benefits><![CDATA[$result[12]]]></benefits>
		<owner>$result[2]</owner>
		<canModify>$canModify</canModify>
	</initiative>
	};

	my @items = split(/\|@/,$result[5]);
	my @flds;
	foreach $item (@items) {
		@flds = split(/\!~/,$item);
		$xml .= qq{<expItem>
		<catId>$flds[0]</catId>
		<category>$flds[1]</category>
		<description><![CDATA[$flds[2]]]></description>
		<qty>$flds[3]</qty>
		<itemPrice>$flds[4]</itemPrice>
		<totalPrice>$flds[5]</totalPrice>
		<fromDate>$flds[6]</fromDate>
		<toDate>$flds[7]</toDate>
	</expItem>
	};
	}
	@items = split(/\|@/,$result[7]);
	foreach $item (@items) {
		@flds = split(/\!~/,$item);
		$xml .= qq{<capItem>
		<catId>$flds[0]</catId>
		<category>$flds[1]</category>
		<description><![CDATA[$flds[2]]]></description>
		<qty>$flds[3]</qty>
		<itemPrice>$flds[4]</itemPrice>
		<totalPrice>$flds[5]</totalPrice>
		<fromDate>$flds[6]</fromDate>
		<toDate>$flds[7]</toDate>
	</capItem>
	};
	}
	@items = split(/\|@/,$result[11]);
	foreach $item (@items) {
		@flds = split(/\!~/,$item);
		$xml .= qq{<timeFrame>
		<phase>$flds[0]</phase>
		<value>$flds[1]</value>
	</timeFrame>
	};
	}
	@items = split(/\|@/,$result[8]);
	foreach $item (@items) {
		my $st=qq{SELECT description FROM initTrackingFormtbl WHERE initId='$item'};
		my $sth=$dbh->prepare($st);
		$sth->execute();
		my $result=$sth->fetchrow_array;
		$xml .= qq{<dependency>
		<id>$item</id>
		<description><![CDATA[$result]]></description>
	</dependency>
	};
	}
	@items = split(/\|@/,$result[10]);
	foreach $item (@items) {
		@flds = split(/\!~/,$item);
		$xml .= qq{<contact>
		<name>$flds[0]</name>
		<telephone>$flds[1]</telephone>
		<organization>$flds[2]</organization>
	</contact>
	};
	}
	
	my $st2=qq{SELECT id,filename FROM attachmentstbl WHERE initId = '$initId'};
	my $sth2=$dbh->prepare($st2);
	$sth2->execute(); 
	while(my(@fileInfo)=$sth2->fetchrow_array) {
		my $filesize = -s "../files/Attachments/$fileInfo[1]";
		$filesize = $filesize / 1024;
		$filesize = "$filesize KB";
		$xml .= qq{<attachment>
		<filename>$fileInfo[1]</filename>
		<size>$filesize</size>
	</attachment>
	};
	}$sth2->finish;
	}
	$xml .= qq{</Initiatives>};
	print $xml;
	#print LOGF $xml;
	#close(LOGF);
}


sub getParams {
	$initId = $cgi->param('initId');
	$teamIndex = $cgi->param('team');
	if($teamIndex ne "") {$teamId = $teamIndex + 1;}
	$owner = $cgi->param('owner');
	$user = $cgi->param('user');
	if($initId ne "") {$whereClause = qq{WHERE initId = '$initId'};}
	else {
		if($teamId > 0) {$whereClause = qq{WHERE teamId = '$teamId'};}
		if($owner ne "" && $whereClause eq "") {$whereClause = qq{WHERE owner = '$owner'};}
		elsif($owner ne "" && $whereClause ne "") {$whereClause .= qq{ AND owner = '$owner'};}
	}
	#my $st=qq{ select * from userstbl where username='$user'};
	#my $sth=$dbh->prepare($st);
	#$sth->execute();
	#my @userInfo =$sth->fetchrow_array;
	#$sth->finish;
	#if($userInfo[1] eq $owner || $userInfo[4] == 1) {$canModify = "true";}
	#else {$canModify = "false";}
}


