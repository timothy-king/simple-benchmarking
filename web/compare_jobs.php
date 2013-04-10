<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
   
<script src="sorttable.js"></script>
<link href="style.css" rel="stylesheet" type="text/css" media="screen" />

   <!--[if IE]><script type="text/javascript" src="excanvas.js"></script><![endif]-->
<script src="js/canvastext.js"></script>
<script src="js/gnuplot_common.js"></script>
<script src="js/gnuplot_mouse.js"></script>
<script src="get_benchmark_name.js" type="text/javascript"> </script>

<link type="text/css" href="js/gnuplot_mouse.css" rel="stylesheet">

<?php
include_once "config.php";   

$reference_job=$_GET['reference'];
$job=$_GET['job'];
   
$xjob = $reference_job;
$yjob = $job;
function generatePlot($xjob, $yjob) {
  // make sure your system is set up to periodically clear the tmp directory 
  $data_file = tempnam(sys_get_temp_dir(), "gnuplotdata");
  $js_map_file = tempnam(sys_get_temp_dir(), "gnuplotdata");
  $js_code = shell_exec('../scripts/scatterPlotWeb.py -xj '.$xjob.' -yj '.$yjob.' -d '.$data_file.' -j '. $js_map_file. ' | gnuplot');
  $js_map_code = file_get_contents($js_map_file); 
  echo $js_code;
  echo $js_map_code;    
}
echo "<script type=\"text/javascript\"> ";
generatePlot($xjob, $yjob); 
echo "</script>";
?>

</head>

<body onload="gnuplot_canvas(); gnuplot.init(); benchmarkInit(); " oncontextmenu="return false;">

<div class="gnuplot">
<table class="plot">
<tr><td>
    <canvas id="gnuplot_canvas" width="800" height="600" tabindex="0">
	Sorry, your browser seems not to support the HTML 5 canvas element
    </canvas>
</td></tr>
</table>

<table class="mbleft">
<tr><td class="mousebox">
<table class="mousebox" border=0>
  <tr><td class="mousebox">
    <table class="mousebox" id="gnuplot_mousebox" border=0>
    <tr><td class="mbh"></td></tr>
    <tr><td class="mbh">
      <table class="mousebox">
	<tr>
	  <td class="icon"></td>
	  <td class="icon" onclick=gnuplot.unzoom><img src="js/previouszoom.png" id="gnuplot_unzoom_icon" class="icon-image" alt="unzoom" title="unzoom"></td>
	  <td class="icon" onclick=gnuplot.rezoom><img src="js/nextzoom.png" id="gnuplot_rezoom_icon" class="icon-image" alt="rezoom" title="rezoom"></td>
	  <td class="icon" onclick=gnuplot.toggle_zoom_text><img src="js/textzoom.png" id="gnuplot_textzoom_icon" class="icon-image" alt="zoom text" title="zoom text with plot"></td>
	</tr>
      </table>
  </td></tr>
</table></td></tr><tr><td class="mousebox">
<table class="mousebox" id="gnuplot_mousebox" border=1>
<tr> <td class="mb0">x&nbsp;</td> <td class="mb1"><span id="gnuplot_canvas_x">&nbsp;</span></td> </tr>
<tr> <td class="mb0">y&nbsp;</td> <td class="mb1"><span id="gnuplot_canvas_y">&nbsp;</span></td> </tr>
<tr> <td class="mb0">benchmark&nbsp;</td> <td class="mb1"><span id="gnuplot_canvas_benchmark">&nbsp;</span></td> </tr>
</table></td></tr>
</table>
</td>

</div>
   

<?php

mysql_connect($server,$user,$password);
@mysql_select_db($database) or die( "Unable to select database");

// getting reference job information 
$query="SELECT * FROM Jobs WHERE id=$reference_job";
$reference_info=mysql_query($query);  
$ref_name=mysql_result($reference_info, 0, 'name');
$ref_description=mysql_result($reference_info, 0, 'description'); 
$ref_time_limit=mysql_result($reference_info, 0, 'time_limit');
$ref_memory_limit=mysql_result($reference_info, 0, 'memory_limit');
$ref_arguments=mysql_result($reference_info, 0, 'arguments');
$ref_timestamp=mysql_result($reference_info, 0, 'timestamp');

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
  <th colspan="6"> Reference Job <?php echo $reference_job ?> </th>
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
  <td> <?php echo $ref_name ?> </td>
  <td> <?php echo $ref_description ?> </td>
  <td> <?php echo $ref_time_limit ?> </td>
  <td> <?php echo $ref_memory_limit ?> </td>
  <td> <?php echo $ref_arguments ?> </td>
  <td> <?php echo $ref_timestamp ?> </td>
	
  </tr>

  </table>

  <br>

  
  <h1> Results </h1>
  <h2> Summary </h2>
  <?php
  $query = "select COUNT(*) from JobResults where job_id = $job and result = \"sat\";"; 
  $num_sat_job = mysql_result(mysql_query($query), 0);

  $query = "select COUNT(*) from JobResults where job_id = $job and result = \"unsat\";"; 
  $num_unsat_job = mysql_result(mysql_query($query), 0);

  $query = "select COUNT(*) from JobResults where job_id = $job and result != \"unsat\" and result !=\"sat\" and run_time > $job_time_limit";
  $num_timeout_job = mysql_result(mysql_query($query), 0);

  $query = "select COUNT(*) from JobResults where job_id = $job and result != \"unsat\" and result !=\"sat\" and memory > $job_memory_limit";
  $num_memout_job = mysql_result(mysql_query($query), 0);


  $query = "select COUNT(*) from JobResults where job_id = $reference_job and result = \"sat\";"; 
  $num_sat_reference = mysql_result(mysql_query($query), 0);

  $query = "select COUNT(*) from JobResults where job_id = $reference_job and result = \"unsat\";"; 
  $num_unsat_reference = mysql_result(mysql_query($query), 0);

  $query = "select COUNT(*) from JobResults where job_id = $reference_job and result != \"unsat\" and result !=\"sat\" and run_time > $ref_time_limit";
  $num_timeout_reference = mysql_result(mysql_query($query), 0);

  $query = "select COUNT(*) from JobResults where job_id = $reference_job and result != \"unsat\" and result !=\"sat\" and memory > $ref_memory_limit";
  $num_memout_reference = mysql_result(mysql_query($query), 0);
  ?>
  
  <table border="1" cellpadding="10">
  <tr>
  <th> </th>
  <th> Job <?php echo $job ?> </th>
  <th> Reference Job <?php echo $reference_job ?> </th>
  </tr>

  <tr>
  <th> SAT solved </th>
  <td> <?php echo $num_sat_job ?> </td>
  <td> <?php echo $num_sat_reference ?> </td>
  </tr>
  <tr>
  <th> UNSAT solved </th>
  <td> <?php echo $num_unsat_job ?></td>
  <td> <?php echo $num_unsat_reference?></td>
  </tr>
  <tr>
  <th> TIMEOUT </th>
  <td> <?php echo $num_timeout_job?></td>
  <td> <?php echo $num_timeout_reference?></td>
  </tr>
  <tr>
  <th> MEMOUT </th>
  <td> <?php echo $num_memout_job?></td>
  <td> <?php echo $num_memout_reference?></td>
  </tr>
  </table>

  
  <?php

  // getting job results

$query="select Problems.path, C.A_run_time, C.A_memory, C.A_result, C.A_exit_status, C.B_run_time, C.B_memory, C.B_result, C.B_exit_status from (select A.problem_id, A.run_time as A_run_time, A.memory as A_memory, A.result as A_result, A.exit_status as A_exit_status, B.run_time as B_run_time, B.memory as B_memory, B.result as B_result, B.exit_status as B_exit_status from (select * from JobResults where job_id=$job) as A inner join (select * from JobResults where job_id = $reference_job) as B on A.problem_id = B.problem_id) as C inner join Problems on Problems.id=C.problem_id;";
$job_results=mysql_query($query);

$i=0;
$num=mysql_numrows($job_results); 
$j=0;
$k=0;
$solved_unsolved=array(); 
$res=array(); 
while ($i < $num) {
  $path = mysql_result($job_results, $i, 'path');
  $job_run_time = mysql_result($job_results, $i, 'A_run_time');
  $job_memory = mysql_result($job_results, $i, 'A_memory');
  $job_result = mysql_result($job_results, $i, 'A_result');
  $job_exit_status = mysql_result($job_results, $i, 'A_exit_status');

  $reference_run_time = mysql_result($job_results, $i, 'B_run_time');
  $reference_memory = mysql_result($job_results, $i, 'B_memory');
  $reference_result = mysql_result($job_results, $i, 'B_result');
  $reference_exit_status = mysql_result($job_results, $i, 'B_exit_status');

  // trying to figure out memouts and timeouts
  // FIXME: this should probably be done when putting the result in the database
  if ($job_result != "sat" and $job_result != "unsat") {
    if ($job_memory > $job_memory_limit) {
      $job_result = "memout"; 
    }
    if ($job_run_time > $job_time_limit) {
      $job_result = "timeout"; 
    }
  }

  if ($reference_result != "sat" and $reference_result != "unsat") {
    if ($reference_memory > $ref_memory_limit) {
      $reference_result = "memout"; 
    }
    if ($reference_run_time > $ref_time_limit) {
      $reference_result = "timeout"; 
    }
  }

  
  
  if ($job_result != $reference_result) {
    $diff_res[$j]['path'] = $path;

    $diff_res[$j]['job_run_time'] = $job_run_time;
    $diff_res[$j]['job_memory'] = $job_memory;
    $diff_res[$j]['job_result'] = $job_result;
    $diff_res[$j]['job_exit_status'] = $job_exit_status;
    
    $diff_res[$j]['reference_run_time'] = $reference_run_time;
    $diff_res[$j]['reference_memory'] = $reference_memory;
    $diff_res[$j]['reference_result'] = $reference_result;
    $diff_res[$j]['reference_exit_status'] = $reference_exit_status;
    ++$j; 
  } else {
    $res[$k]['path'] = $path;

    $res[$k]['job_run_time'] = $job_run_time;
    $res[$k]['job_memory'] = $job_memory;
    $res[$k]['job_result'] = $job_result;
    $res[$k]['job_exit_status'] = $job_exit_status;
    
    $res[$k]['reference_run_time'] = $reference_run_time;
    $res[$k]['reference_memory'] = $reference_memory;
    $res[$k]['reference_result'] = $reference_result;
    $res[$k]['reference_exit_status'] = $reference_exit_status;
    ++$k; 
  }
  $i++;
}
  
mysql_close();
?>

<h2> Different Results </h2>

<table class="sortable" border="1" cellpadding="5">
  <tr>
  <th> # </th>
  <th> Benchmark </th>
  <th> Run Time </th>
  <th> Memory</th>
  <th> Result </th>
  <th> Exit </th>
  <th> Ref Run Time </th>
  <th> Ref Memory</th>
  <th> Ref Result </th>
  <th> Ref Exit </th>
  </tr>

  <?php
  $i = 0;
$num = count($diff_res);
while ($i < $num ) {
  ?>
    
  <tr>
    <td> <?php echo $i ?> </td>
    <td> <?php echo $diff_res[$i]['path'] ?> </td>
    
    <td> <?php echo $diff_res[$i]['job_run_time'] ?> </td>
    <td> <?php echo $diff_res[$i]['job_memory'] ?> </td>
    <td> <?php echo $diff_res[$i]['job_result'] ?> </td>
    <td> <?php echo $diff_res[$i]['job_exit_status'] ?> </td>

    <td> <?php echo $diff_res[$i]['reference_run_time'] ?> </td>
    <td> <?php echo $diff_res[$i]['reference_memory'] ?> </td>
    <td> <?php echo $diff_res[$i]['reference_result'] ?> </td>
    <td> <?php echo $diff_res[$i]['reference_exit_status'] ?> </td>

    </tr>

   

    <?php
    $i++; 
}
   
?>

</table>

<h2> Same Results </h2>
   
<table class="sortable" border="1" cellpadding="5">
  <tr>
  <th> # </th>
  <th> Benchmark </th>
  <th> Run Time </th>
  <th> Memory</th>
  <th> Result </th>
  <th> Exit </th>
  <th> Ref Run Time </th>
  <th> Ref Memory</th>
  <th> Ref Result </th>
  <th> Ref Exit </th>
  </tr>

  <?php
  $i = 0;
$num = count($res);
while ($i < $num ) {
  ?>
    
  <tr>
    <td> <?php echo $i ?> </td>
    <td> <?php echo $res[$i]['path'] ?> </td>
    
    <td> <?php echo $res[$i]['job_run_time'] ?> </td>
    <td> <?php echo $res[$i]['job_memory'] ?> </td>
    <td> <?php echo $res[$i]['job_result'] ?> </td>
    <td> <?php echo $res[$i]['job_exit_status'] ?> </td>

    <td> <?php echo $res[$i]['reference_run_time'] ?> </td>
    <td> <?php echo $res[$i]['reference_memory'] ?> </td>
    <td> <?php echo $res[$i]['reference_result'] ?> </td>
    <td> <?php echo $res[$i]['reference_exit_status'] ?> </td>
    <?php
    $i++; 
}
   
?>
</table>
</body>
</html>
