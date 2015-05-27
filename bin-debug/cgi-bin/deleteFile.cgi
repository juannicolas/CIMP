#!/usr/bin/perl
use CGI qw(:standard);

require "/home/weoms/proc/globals/connDB.pl";

$|=1;
$cgi=new CGI;
print "Content-type: text/html\n\n";
my $dbh=connACITPdb();
$dir = "../files/Attachments";
$filename = $cgi->param("filename");


$success = "true";
$error = "Delete failed for file: $filename";
unlink("$dir/$filename") or $success  = "false";

if($success eq "true") {
	my $st=qq{DELETE FROM attachmentstbl WHERE filename = '$filename'};
	my $sth=$dbh->prepare($st);
	$sth->execute(); $sth->finish;
	$error="";
}
$xml = qq{<?xml version="1.0" encoding="utf-8"?>
<results>
	<success>$success</success>
	<errmsg>$error</errmsg>
</results>
};
print $xml;

exit 0;