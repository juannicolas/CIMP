#!/usr/bin/perl
use CGI qw(:standard);

require "/home/weoms/proc/globals/connDB.pl";


$|=1;
$cgi=new CGI;
print "Content-type: text/html\n\n";
my $dbh=connACITPdb();
my $dbdate=`date '+%Y-%m-%d %H:%M:%S'`; chomp $dbdate;
if( $cgi->param()){
	$admin="";
	$action= $cgi->param('action');
	getParams();
	if($action eq "logAdd") {procAdd();}
	elsif($action eq "logSave"){procSave();}
	elsif($action eq "logDel"){procDel();}
	elsif($action eq "logSearch"){print getXML();}
}
else {
	print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: No data was sent to server</msg></error></Results>};
}
$dbh->disconnect;
exit 0;


sub procAdd {
	my $err = 0;
	$st=qq{INSERT INTO userLogstbl VALUES('','$dbdate','$owner','$initId','$log','$teamId')};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	$logId= $dbh->last_insert_id(undef, undef, qw(userLogstbl initId)) or $err = 1;
	if ($logId <= 0 || $err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot add log entry</msg></error></Results>}; return 0;}
	else {
		$st=qq{INSERT INTO transactions VALUES('','$dbdate','$user','5','Added Log Entry# $logId')};
		$sth=$dbh->prepare($st);
		$sth->execute(); $sth->finish;
		print getXML();
	}
	
}

sub procSave {
	my $err = 0;
	$st=qq{UPDATE userLogstbl SET initId='$initId',logNotes='$log',teamId='$teamId' WHERE id='$logId'};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot modify log</msg></error></Results>}; return 0;}
	else {
		$st=qq{INSERT INTO transactions VALUES('','$dbdate','$user','6','Modified Log Entry# $logId')};
		$sth=$dbh->prepare($st);
		$sth->execute(); $sth->finish;
		print getXML();
	}
}

sub procDel {
	my $err = 0;
	$st=qq{DELETE FROM userLogstbl WHERE id='$logId'};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot delete log</msg></error></Results>}; return 0;}
	else {
		$st=qq{INSERT INTO transactions VALUES('','$dbdate','$user','7','Deleted Log Entry# $logId')};
		$sth=$dbh->prepare($st);
		$sth->execute(); $sth->finish;
		clearParams();
		print getXML();
	}
}

sub getParams {
	$logId = $cgi->param('id');
	$initId = $cgi->param('initId');
	$teamIndex = $cgi->param('team');
	$teamId = $teamIndex + 1;
	$log = $cgi->param('log');
	$owner = $cgi->param('owner');
	$user = $cgi->param('user');
	$searchInitId = $cgi->param('sInitId');
	$searchTeamId = $cgi->param('sTeam');
	$searchOwner = $cgi->param('sOwner');
	$searchFromDate = $cgi->param('fromDate');
	$searchToDate = $cgi->param('toDate');
	if($searchFromDate eq "" && $searchToDate ne "") {$searchFromDate = $searchToDate;}
	if($searchFromDate ne "" && $searchToDate eq "") {$searchToDate = $searchFromDate;}
	if($searchFromDate ne "") {
		my @dateFlds=split("/",$searchFromDate);
		$searchFromDate = "$dateFlds[2]-$dateFlds[0]-$dateFlds[1]";
		@dateFlds=split("/",$searchToDate);
		$searchToDate = "$dateFlds[2]-$dateFlds[0]-$dateFlds[1]";
	}
	if($searchInitId ne "") {$whereClause = qq{WHERE initId = '$searchInitId'};}
	else {
		if($searchTeamId > 0) {$whereClause = qq{WHERE teamId = '$searchTeamId'};}
		if($searchOwner ne "" && $whereClause eq "") {$whereClause = qq{WHERE owner = '$searchOwner'};}
		elsif($searchOwner ne "" && $whereClause ne "") {$whereClause .= qq{ AND owner = '$searchOwner'};}
		if($searchFromDate ne "" && $whereClause eq "") {$whereClause = qq{WHERE date >= '$searchFromDate' AND date <= '$searchToDate'};}
		elsif($searchFromDate ne "" && $whereClause ne "") {$whereClause = qq{WHERE date >= '$searchFromDate' AND date <= '$searchToDate'};}
	}
	
	my $st=qq{ select privilege from userstbl where username='$user'};
	my $sth=$dbh->prepare($st);
	$sth->execute();
	my $privilege=$sth->fetchrow_array;
	$sth->finish;
	if($privilege == 1) {$admin = "true";}
	else {$admin = "false";}
	
}

sub clearParams {
	$logId = "";
	$initId = "";
	$teamIndex = "";
	$teamId = "";
	$log = "";
	$owner = "";
	$user = "";
}

sub getXML {
	#open(LOGF,">log.xml");
	my $err = 0;
	my $st=qq{SELECT * FROM userLogstbl $whereClause};
	#print LOGF "$st\n";
	my $sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><error><msg>Error: Cannot search for logs</msg></error></Results>}; return 0;}
	my $xml =qq{<?xml version="1.0" encoding="utf-8"?>
<Logs>
	<success>true</success>
	};
	while(my(@result)=$sth->fetchrow_array) {
		$st=qq{SELECT name FROM teamstbl WHERE id = '$result[5]'};
		$sth2=$dbh->prepare($st);
		$sth2->execute();
		my $teamName=$sth2->fetchrow_array;
		$result[5] = $result[5] - 1;
		if($result[3] <= 0) {$result[3]="";}
		$st=qq{ select fullName from userstbl where username='$result[2]'};
		$sth2=$dbh->prepare($st);
		$sth2->execute();
		my $ownerFullName=$sth2->fetchrow_array;
		$sth2->finish;
		my $canModify = "true";
		if($admin eq "false") {
			if($result[2] eq $user) {$canModify = "true";}
			else {$canModify = "false";}
		}
		$xml .=qq{<log>
		<id>$result[0]</id>
		<date>$result[1]</date>
		<team>$result[5]</team>
		<teamName><![CDATA[$teamName]]></teamName>
		<initId>$result[3]</initId>
		<logNotes><![CDATA[$result[4]]]></logNotes>
		<owner><![CDATA[$ownerFullName]]></owner>
		<canModify>$canModify</canModify>
	</log>
	};
	}
	$xml .= qq{</Logs>};
	#print LOGF $xml;
	#close(LOGF);
	return $xml;
}

