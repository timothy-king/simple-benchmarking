<html>
<head>
<script src="sorttable.js"></script>
   <link href="style.css" rel="stylesheet" type="text/css" media="screen" />
   </head>

   <body>


   <?php

$user_file="../config/user";
$password_file="../config/password";

$user=trim(file_get_contents($user_file));
$password=trim(file_get_contents($password_file));
$database="benchmarking";


$statistic=$_GET['statistic'];
$statistic=mysql_real_escape_string($statistic); 
$job=$_GET['job'];
$ref_job=$_GET['reference'];
 
mysql_connect("localhost",$user,$password);
@mysql_select_db($database) or die( "Unable to select database");

// getting job information 
$query="SELECT * FROM Jobs WHERE id=$job";
$job_info=mysql_query($query);
$job_name=mysql_result($job_info, 0, 'name');
$job_description=mysql_result($job_info, 0, 'description'); 
$job_time_limit=mysql_result($job_info, 0, 'time_limit');
$job_memory_limit=mysql_result($job_info, 0, 'memory_limit');
$job_arguments=mysql_result($job_info, 0, 'arguments');
$job_timestamp=mysql_result($job_info, 0, 'timestamp');

// getting reference job information

$query="SELECT * FROM Jobs WHERE id=$ref_job";
$ref_job_info=mysql_query($query);
$ref_job_name=mysql_result($ref_job_info, 0, 'name');
$ref_job_description=mysql_result($ref_job_info, 0, 'description'); 
$ref_job_time_limit=mysql_result($ref_job_info, 0, 'time_limit');
$ref_job_memory_limit=mysql_result($ref_job_info, 0, 'memory_limit');
$ref_job_arguments=mysql_result($ref_job_info, 0, 'arguments');
$ref_job_timestamp=mysql_result($ref_job_info, 0, 'timestamp');

// displaying job information table
?>

<table border="1" cellpadding="10">
  <tr>
  <th colspan="6"> Job <?php echo $job ?> </th>
  <th colspan="6"> Reference Job <?php echo $ref_job ?> </th>
  </tr>

  <tr>
  <th> Name </th>
  <th> Description </th>
  <th> T/O </th>
  <th> M/O </th>
  <th> Args </th>
  <th> Time </th>
  <th> Name </th>
  <th> Description </th>
  <th> T/O </th>
  <th> M/O </th>
  <th> Args </th>
  <th> Time </th>
  </tr>

  <tr>
  <td> <?php echo $job_name ?> </td>
  <td> <?php echo $job_description ?> </td>
  <td> <?php echo $job_time_limit ?> </td>
  <td> <?php echo $job_memory_limit ?> </td>
  <td> <?php echo $job_arguments ?> </td>
  <td> <?php echo $job_timestamp ?> </td>
  <td> <?php echo $ref_job_name ?> </td>
  <td> <?php echo $ref_job_description ?> </td>
  <td> <?php echo $ref_job_time_limit ?> </td>
  <td> <?php echo $ref_job_memory_limit ?> </td>
  <td> <?php echo $ref_job_arguments ?> </td>
  <td> <?php echo $ref_job_timestamp ?> </td>
	
  </tr>

  </table>

  <br>

  <h1> Stats </h1>

<?php
$query="SELECT id, problem_id FROM JobResults WHERE job_id=$job";
$job_result=mysql_query($query);

$query="SELECT id, problem_id FROM JobResults WHERE job_id=$ref_job";
$ref_job_result=mysql_query($query);

$query="SELECT id, name FROM Stats WHERE name LIKE \"$statistic\"";
$stat=mysql_query($query);
$stat_id=mysql_result($stat, 0, 'id'); 
$stat_name=mysql_result($stat, 0, 'name'); 
// table header 
?>
<table border="1" cellpadding="5">
  <tr>
  <th> # </th>
  <th> Benchmark </th>
  <th> Job <?php echo $stat_name ?> </th>
  <th> Reference <?php echo $stat_name ?> </th>
</tr>

<?php
$j = 0;
$num_res=mysql_numrows($job_result);
// iterating through benchmarks
while ($j < $num_res) {
  $job_res_id=mysql_result($job_result, $j, 'id');
  $benchmark_id=mysql_result($job_result, $j, 'problem_id');
  $query="SELECT path FROM Problems WHERE id=$benchmark_id";
  $path_res = mysql_query($query);
  $path=mysql_result($path_res, 0); 
  $i = 0;

  // getting statistic value for job
  $query="SELECT stat_value FROM ResultStats WHERE job_result_id=$job_res_id AND stat_id = $stat_id";
  $stat_value_res=mysql_query($query);
  if(mysql_numrows($stat_value_res) > 0) { 
    $stat_value=mysql_result($stat_value_res, 0);

    // getting statistic value for reference job 
    $ref_result_id_res=mysql_query("SELECT id FROM JobResults WHERE job_id = $ref_job AND problem_id=$benchmark_id");

    if (mysql_numrows($ref_result_id_res) > 0) {
      $ref_result_id=mysql_result($ref_result_id_res, 0); 
      $ref_stat_value_res=mysql_query("SELECT stat_value FROM ResultStats WHERE job_result_id=$ref_result_id AND stat_id =$stat_id");
      if (mysql_numrows($ref_stat_value_res) > 0) {
	$ref_stat_value = mysql_result($ref_stat_value_res, 0);
      } else {
	$ref_stat_value="N/A"; 
      }
    } else {
      $ref_stat_value="N/A"; 
    }
  } else {
    $stat_value = "N/A"; 
  }
?>

  <tr>
    <td> <?php echo $j ?> </td>
    <td> <?php echo $path ?> </td>
    <td> <?php echo $stat_value ?> </td>
    <td> <?php echo $ref_stat_value ?> </td>
  </tr>
<?php
  $j++;
}
?>
</table>
    
</body>
</html>
