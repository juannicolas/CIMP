#!/usr/bin/perl
use CGI qw(:standard);

require "/home/weoms/proc/globals/connDB.pl";


$|=1;
$cgi=new CGI;
print "Content-type: text/html\n\n";
my $dbh=connACITPdb();
my $dbdate=`date '+%Y-%m-%d %H:%M:%S'`; chomp $dbdate;
if( $cgi->param()){
	$canModify = "true";
	$action= $cgi->param('action');
	getParams();
	if($action eq "Add") {procAdd();}
	elsif($action eq "Save"){procSave();}
	elsif($action eq "Delete"){procDel();}
}
else {
	print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: No data was sent to server</msg></error></Results>};
}
$dbh->disconnect;
exit 0;


sub procAdd {
	my $err = 0;
	$st=qq{INSERT INTO initTrackingFormtbl VALUES('','$teamId','$owner','$description','$dbexpense','$expItems','$dbcapital','$capItems','$dependIds','$dependNotes','$contacts','$timeFrames','$benefits','$expDesc','$capDesc')};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	$initId = $dbh->last_insert_id(undef, undef, qw(initTrackingFormtbl initId)) or $err = 1;
	if ($initId <= 0 || $err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot add initiative</msg></error></Results>}; return 0;}
	else {
		$st=qq{INSERT INTO transactions VALUES('','$dbdate','$user','2','Added Initiative# $initId')};
		$sth=$dbh->prepare($st);
		$sth->execute(); $sth->finish;
		print getXML();
	}
	
}

sub procSave {
	my $err = 0;
	$st=qq{UPDATE initTrackingFormtbl SET teamId='$teamId',owner='$owner',description='$description',expenseTotal='$dbexpense',expenseItems='$expItems',capitalTotal='$dbcapital',capitalItems='$capItems',dependIds='$dependIds',dependNotes='$dependNotes',contacts='$contacts',timeFrames='$timeFrames',benefits='$benefits',expDesc='$expDesc',capDesc='$capDesc' WHERE initId='$initId'};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot modify initiative</msg></error></Results>}; return 0;}
	else {
		$st=qq{INSERT INTO transactions VALUES('','$dbdate','$user','3','Modified Initiative# $initId')};
		$sth=$dbh->prepare($st);
		$sth->execute(); $sth->finish;
		print getXML();
	}
}

sub procDel {
	my $err = 0;
	$st=qq{DELETE FROM initTrackingFormtbl WHERE initId = '$initId'};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	
	$st=qq{SELECT filename FROM attachmentstbl WHERE initId = '$initId'};
	$sth=$dbh->prepare($st);
	$sth->execute(); 
	while(my($filename)=$sth->fetchrow_array) {
		unlink("../files/Attachments/$filename");
	}$sth->finish;
	
	$st=qq{DELETE FROM attachmentstbl WHERE initId = '$initId'};
	$sth=$dbh->prepare($st);
	$sth->execute(); $sth->finish;
	
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot delete initiative</msg></error></Results>}; return 0;}
	else {
		$st=qq{INSERT INTO transactions VALUES('','$dbdate','$user','4','Deleted Initiative# $initId')};
		$sth=$dbh->prepare($st);
		$sth->execute(); $sth->finish;
		clearParams();
		print getXML();
	}
}

sub getParams {
	$initId = $cgi->param('initId');
	$teamIndex = $cgi->param('team');
	$teamId = $teamIndex + 1;
	$description = $cgi->param('description');
	$expense = $cgi->param('expense');
	$dbexpense = $expense;
	$dbexpense =~ tr/$,//d;
	$expDesc = $cgi->param('expDesc');
	$capital = $cgi->param('capital');
	$dbcapital = $capital;
	$dbcapital =~ tr/$,//d;
	$capDesc = $cgi->param('capDesc');
	$dependNotes = $cgi->param('dependNotes');
	$benefits = $cgi->param('benefits');
	$owner = $cgi->param('owner');
	$user = $cgi->param('user');
	$expItems = $cgi->param('expItems');
	$capItems = $cgi->param('capItems');
	$timeFrames = $cgi->param('timeFrames');
	$dependIds = $cgi->param('dependIds');
	$contacts = $cgi->param('contacts');
}

sub clearParams {
	$initId = "";
	$teamIndex = "";
	$teamId = "";
	$description = "";
	$expense = "";
	$dbexpense = "";
	$expDesc = "";
	$capital = "";
	$dbcapital = "";
	$capDesc = "";
	$dependNotes = "";
	$benefits = "";
	$owner = "";
	$user = "";
	$expItems = "";
	$capItems = "";
	$timeFrames = "";
	$dependIds = "";
	$contacts = "";
}

sub getXML {
	my $success = qq{<procResult><value>true</value><prevAction>$action</prevAction></procResult>};
	my $xml =qq{<?xml version="1.0" encoding="utf-8"?>
<Initiatives>
	$success
	<initiative>
		<id>$initId</id>
		<team>$teamIndex</team>
		<description><![CDATA[$description]]></description>
		<expense>$expense</expense>
		<expDesc><![CDATA[$expDesc]]></expDesc>
		<capital>$capital</capital>
		<capDesc><![CDATA[$capDesc]]></capDesc>
		<dependNotes>$dependNotes</dependNotes>
		<benefits>$benefits</benefits>
		<owner>$owner</owner>
		<canModify>$canModify</canModify>
	</initiative>
	};

	my @items = split(/\|@/,$expItems);
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
	@items = split(/\|@/,$capItems);
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
	@items = split(/\|@/,$timeFrames);
	foreach $item (@items) {
		@flds = split(/\!~/,$item);
		$xml .= qq{<timeFrame>
		<phase>$flds[0]</phase>
		<value>$flds[1]</value>
	</timeFrame>
	};
	}
	@items = split(/\|@/,$dependIds);
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
	@items = split(/\|@/,$contacts);
	foreach $item (@items) {
		@flds = split(/\!~/,$item);
		$xml .= qq{<contact>
		<name>$flds[0]</name>
		<telephone>$flds[1]</telephone>
		<organization>$flds[2]</organization>
	</contact>
	};
	}
	$xml .= qq{</Initiatives>};
	return $xml;
}

