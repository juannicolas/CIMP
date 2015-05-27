#!/usr/bin/perl
use CGI qw(:standard);
use Date::Calc qw(:all);


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
	my @timeType=("Years","Months","Weeks","Days");
	my @Months=("","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dic");
	$st=qq{SELECT * FROM initTrackingFormtbl $whereClause};
	$sth=$dbh->prepare($st) or $err = 1;
	$sth->execute() or $err = 1;
	if ($err) {print qq{<?xml version="1.0" encoding="utf-8"?><Results><success>false</success><error><msg>Error: Cannot search for initiatives</msg></error></Results>}; return 0;}
	my $xml =qq{<?xml version="1.0" encoding="utf-8"?>
<SummaryReport>
	<success>true</success>
	};
	#open(LOGF,">log.xml");
	my $total = 0; my %hMonthSum=();
	while(my(@result)=$sth->fetchrow_array) {
		$totalTframe = ""; %hTimeFrame={};
		$result[4] =~ s/\G(\d{1,3})(?=(?:\d\d\d)+(?:\.|$))/$1,/g;
		$result[4] = '$' . $result[4];
		$result[6] =~ s/\G(\d{1,3})(?=(?:\d\d\d)+(?:\.|$))/$1,/g;
		$result[6] = '$' . $result[6];
		$st=qq{SELECT name FROM teamstbl WHERE id = '$result[1]'};
		$sth2=$dbh->prepare($st);
		$sth2->execute();
		my $teamName=$sth2->fetchrow_array;
		$st=qq{ select fullName from userstbl where username='$result[2]'};
		$sth2=$dbh->prepare($st);
		$sth2->execute();
		my $ownerFullName=$sth2->fetchrow_array;
		$sth2->finish;
		@items = split(/\|@/,$result[11]);
		foreach $item (@items) {
			my @flds = split(/\!~/,$item);
			my @flds2 = split(/\s+/,$flds[1]);
			$hTimeFrame{$flds2[1]} += $flds2[0];
		}
		foreach $type (@timeType){ if(exists $hTimeFrame{$type}) {$totalTframe .= "$hTimeFrame{$type} $type, ";}}
		
		for(1..2) {
			my $type = "";
			if($_ == 1) {@items = split(/\|@/,$result[5]); $type="Exp";}
			else {@items = split(/\|@/,$result[7]); $type="Cap";}
			foreach $item (@items) {
				my @flds = split(/\!~/,$item);
				$flds[5] =~ tr/$,//d;
				my @dateFlds1 = split("/",$flds[6]);
				$flds[6] = "$dateFlds1[2]-$dateFlds1[0]-$dateFlds1[1]";
				my @dateFlds2 = split("/",$flds[7]);
				$flds[7] = "$dateFlds2[2]-$dateFlds2[0]-$dateFlds2[1]";
				my $dd = Delta_Days($dateFlds1[2],$dateFlds1[0],$dateFlds1[1],$dateFlds2[2],$dateFlds2[0],$dateFlds2[1]);
				if($dd <= 0) {$dd = 1;}
				my $dailyTotal = $flds[5]/$dd;
				my $currDate = $flds[6];
				my $lastDate = GetNextDay($flds[7]);
				while($currDate ne $lastDate) {
					my @dateFlds=split("-",$currDate);
					my $currMonth = "$dateFlds[0]-$dateFlds[1]";
					$hMonthSum{$currMonth}{$type} += $dailyTotal;
					$currDate = GetNextDay($currDate);		
				}			
			}
		}
		
		$xml .= qq{<initiative>
		<id>$result[0]</id>
		<team><![CDATA[$result[1]. $teamName]]></team>
		<description><![CDATA[$result[3]]]></description>
		<expense><![CDATA[$result[4]]]></expense>
		<capital><![CDATA[$result[6]]]></capital>
		<totalTframe><![CDATA[$totalTframe]]></totalTframe>
		<owner>$ownerFullName</owner>
	</initiative>
	};
		$total++;
	}
	
	foreach $month (sort keys %hMonthSum) {
		my @monthFlds=split("-",$month);
		my $currMonth = "$Months[$monthFlds[1]]$monthFlds[0]";
		$hMonthSum{$month}{"Exp"}=sprintf("%.2f",$hMonthSum{$month}{"Exp"});
		$hMonthSum{$month}{"Cap"}=sprintf("%.2f",$hMonthSum{$month}{"Cap"});
	$xml .= qq{<summItem>
		<month>$currMonth</month>
	        <expense>$hMonthSum{$month}{"Exp"}</expense>
	        <capital>$hMonthSum{$month}{"Cap"}</capital>
	    </summItem>
	};
	}

	$xml .= qq{<total>$total</total></SummaryReport>};
	print $xml;
	#print LOGF $xml;
	#close(LOGF);
}




sub getParams {
	$initId = $cgi->param('initId');
	$teamId = $cgi->param('team');
	$owner = $cgi->param('owner');
	if($initId ne "") {$whereClause = qq{WHERE initId = '$initId'};}
	else {
		if($teamId > 0) {$whereClause = qq{WHERE teamId = '$teamId'};}
		if($owner ne "" && $whereClause eq "") {$whereClause = qq{WHERE owner = '$owner'};}
		elsif($owner ne "" && $whereClause ne "") {$whereClause .= qq{ AND owner = '$owner'};}
	}
}

sub GetNextDay {
        my $date=shift;
        ($year,$month,$day)=split("-",$date);
        ($yearnew,$monthnew,$daynew) = Add_Delta_Days($year,$month,$day,+1);

        if(length($monthnew)==1) { $monthnew = "0".$monthnew; }
        if(length($daynew)==1) { $daynew = "0".$daynew; }
        my $return = "$yearnew-$monthnew-$daynew";
        return $return;
}


