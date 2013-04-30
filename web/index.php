<!DOCTYPE html>
<html>
<head>
<script src="sorttable.js"></script>
   <link href="style.css" rel="stylesheet" type="text/css" media="screen" />
   </head>
   <body>

   <h1> Compare Jobs </h1>
   <table border="0" cellpadding="5">
   <tr>
   <form action="compare_jobs.php" method="get">
   <td> Reference job: </td>
   <td> <input type="text" name="reference" size="6" align="right"> </td>
   </tr>
   <tr>
   <td>Job:  </td>
   <td> <input type="text" name="job" size="6" align="left"> </td>
   </tr>
   </table>
   <input type="Submit">
   </form>
   
   <hr />


   <h1> Get Statistics </h1>
   <table border="0" cellpadding="5"> 
   <form action="stats.php" method="get">
   <tr>
   <td> Job: </td>
   <td> <input type="text" name="job"> </td>
   </tr>
   <tr>
   <td> Statistics: </td>
   <td> <input type="text" name="statistic"> </td>
   </tr>
   </table>
   <input type="Submit">
   </form>

   <hr />

   <h1> Compare Statistics </h1>
   <table border="0" cellpadding="5"> 
   <form action="compare_stats.php" method="get">
   <tr>
   <td> Reference Job: </td>
   <td> <input type="text" name="reference"> </td>
   </tr>

   <tr>
   <td> Job: </td>
   <td> <input type="text" name="job"> </td>
   </tr>

   <tr>
   <td> Statistic: </td>
   <td> <input type="text" name="statistic" ></td>
   </tr>
   </table>
   <input type="Submit">
   </form>

      <hr />

   <h1> Generate Cactus Plot </h1>
   
   <table border="0" cellpadding="5"> 
   <form action="generate_cacti.php" method="get">
   <tr>
   <td> Job Ids: </td>
   <td> <input type="text" name="job_ids"> </td>
   </tr>
   </table>

   <input type="Submit">
   </form>

	<hr />

<p>
<strong>View recently-completed CVC4 cluster jobs:</strong><br/>
<?php
include_once "config.php";

mysql_connect($server,$user,$password);
@mysql_select_db($database) or die( "Unable to select database");

  $query = "select * from Jobs where Jobs.timestamp > subtime(now(), '72:00:00')";
  $result = mysql_query($query);
  $rows = mysql_num_rows($result);
  if($rows == 0) {
    echo "<br/>No jobs finished in the last seventy-two hours.\n";
  } else {
    echo $rows." job".($rows > 1 ? 's' : '')." submitted in the last seventy-two hours.\n";
    while($job = mysql_fetch_assoc($result)) {
	$url = "";
      //$url = mkurl($job['id'], find_ref_job($job));
      //$onmouseinout = "onmouseover=\"document.getElementById('fcompare".$job['id']."').style.visibility = 'visible';\" onmouseout=\"document.getElementById('fcompare".$job['id']."').style.visibility = 'hidden';\"";
      echo "<li> <a href=\"$url\" title=\"".htmlentities($job['description'].$job['arguments'])."\">".$job['id']."</a> (".$job['name'].", submitted ".$job['timestamp'].")</div>\n";
    }
  }
  mysql_free_result($result);
?>
</p>

   
   </body>
   </html>
