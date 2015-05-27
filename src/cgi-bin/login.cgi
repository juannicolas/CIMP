#!/usr/bin/perl
use DBI;
use CGI qw(:standard);
use LWP::Simple;

require "/home/weoms/proc/globals/connDB.pl";

$|=1;
$cgi=new CGI;
print "Content-type: text/html\n\n";
my $dbdate=`date '+%Y-%m-%d %H:%M:%S'`; chomp $dbdate;
my $ip = $ENV{'REMOTE_ADDR'};
if( $cgi->param()){
	($user, $passwd)=( $cgi->param('username'),$cgi->param('passwd'));
	#print "$user $passwd - ";
	my $dbh=connACITPdb(); 
	$st=qq{ select * from userstbl where username='$user' and passwd=password('$passwd')};
	$sth=$dbh->prepare($st);
	$sth->execute();
	@result =$sth->fetchrow_array;
	$sth->finish;
	if($#result > 0) {
		$st=qq{INSERT INTO transactions VALUES('','$dbdate','$user','1','Logged in from $ip')};
		$sth=$dbh->prepare($st);
		$sth->execute(); $sth->finish;
		print "true";
	}
	else {print "false";}
	$dbh->disconnect;
}
else{print "false";}
exit 0;