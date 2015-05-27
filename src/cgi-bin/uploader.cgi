#!/usr/bin/perl
use CGI qw(:standard);

require "/home/weoms/proc/globals/connDB.pl";

$|=1;
$cgi=new CGI;
print "Content-type: text/html\n\n";
my $dbh=connACITPdb();
$upload_dir = "../files/Attachments";
$initId = $cgi->param("initId");
$owner = $cgi->param("owner");
$filename = $cgi->param("Filedata");
$filename =~ s/.*[\/\\](.*)/$1/;
$filename = "$initId-$owner-$filename";

$upload_filehandle = $cgi->upload("Filedata");
$success = "true";
$error = "Upload failed for file: $filename";

open(UPLOADFILE, ">$upload_dir/$filename") or $success  = "false";
binmode UPLOADFILE;
while ( <$upload_filehandle> ){print UPLOADFILE $_;}
close(UPLOADFILE);
if($success eq "true") {
	my $st=qq{INSERT INTO attachmentstbl VALUES('','$initId','$filename','$owner')};
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