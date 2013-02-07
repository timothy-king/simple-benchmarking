<html>
<head>
<script src="sorttable.js"></script>
   <link href="style.css" rel="stylesheet" type="text/css" media="screen" />
   </head>

   <body>


   <?php

include_once "config.php";

$statistic=$_GET['statistic'];
$statistic=mysql_real_escape_string($statistic); 

$statistic='"' .  $statistic . '"'; 
$statistic=str_replace(', ', '" OR name LIKE "', $statistic);


$job=$_GET['job'];
       
mysql_connect($server,$user,$password);
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

// displaying job information table
?>

<table border="1" cellpadding="10">
  <tr>
  <th colspan="6"> Job <?php echo $job ?> </th>
  </tr>

  <tr>
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
  </tr>

  </table>

  <br />

  <h1> Stats </h1>

<?php
$query="SELECT id, problem_id FROM JobResults WHERE job_id=$job";
$job_result=mysql_query($query);
$query="SELECT * FROM Stats WHERE name LIKE $statistic";
$stats=mysql_query($query);

$i = 0;
$num_stats = mysql_numrows($stats);
// table header 
?>
<table class="sortable" border="1" cellpadding="5">
  <tr>
  <th> # </th>
  <th> Benchmark </th>
  <?php
  while ($i < $num_stats) {
    ?>
    <th> <?php echo mysql_result($stats, $i, 'name') ?></th>
    <?php
    $i++;
  }
?>
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

  $query="SELECT stat_id, stat_value FROM ResultStats WHERE job_result_id=$job_res_id";
  $benchmark_stats=mysql_query($query);
  
  // construct a map based on the current benchmark's statistics
  $k = 0;
  $num_bench_stats = mysql_numrows($benchmark_stats);
  $bench_map=array(); 
  while ($k < $num_bench_stats) {
    $stat_id = mysql_result($benchmark_stats, $k, 'stat_id');
    $stat_value = mysql_result($benchmark_stats, $k, 'stat_value');
    $bench_map[$stat_id] = $stat_value; 
    $k++; 
  }
?>

  <tr>
    <td> <?php echo $j ?> </td>
    <td> <?php echo $path ?> </td>
  <?php
  while ($i<$num_stats) {
    $stat_id=mysql_result($stats, $i, 'id');
    if (array_key_exists($stat_id, $bench_map)) {
	$stat_value = $bench_map[$stat_id]; 
      } else {
	$stat_value = "N/A"; 
      }
  ?>
    
    <td> <?php echo $stat_value ?> </td>
       
  <?php
    $i++;
  }
  ?>
  </tr>
<?php
  $j++;
}
?>
</table>
    
</body>
</html>
