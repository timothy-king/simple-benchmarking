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
   
$xjob = $job;
$yjob = $reference_job; 
function generatePlot($xjob, $yjob) {
  // make sure your system is set up to periodically clear the tmp directory 
  $data_file = tempnam(sys_get_temp_dir(), "gnuplotdata");
  $js_map_file = tempnam(sys_get_temp_dir(), "gnuplotdata");
  $js_code = shell_exec('../scripts/generateGnuPlotCommand.py -xj '.$xjob.' -yj '.$yjob.' -d '.$data_file.' -j '. $js_map_file. ' | gnuplot');
  $js_map_code = file_get_contents($js_map_file); 
  echo $js_code;
  echo $js_map_code;    
  shell_exec('rm $temp_file'); 
}
echo "<script type=\"text/javascript\"> ";
generatePlot($xjob, $yjob); 
echo "</script>";
?>

</head>

<body onload="gnuplot_canvas(); gnuplot.init(); benchmarkInit(); " oncontextmenu="return false;">

<div class="gnuplot">
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
	  <td class="icon" onclick=gnuplot.toggle_grid><img src="js/grid.png" id="gnuplot_grid_icon" class="icon-image" alt="#" title="toggle grid"></td>
	  <td class="icon" onclick=gnuplot.unzoom><img src="js/previouszoom.png" id="gnuplot_unzoom_icon" class="icon-image" alt="unzoom" title="unzoom"></td>
	  <td class="icon" onclick=gnuplot.rezoom><img src="js/nextzoom.png" id="gnuplot_rezoom_icon" class="icon-image" alt="rezoom" title="rezoom"></td>
	  <td class="icon" onclick=gnuplot.toggle_zoom_text><img src="js/textzoom.png" id="gnuplot_textzoom_icon" class="icon-image" alt="zoom text" title="zoom text with plot"></td>
	  <td class="icon" onclick=gnuplot.popup_help()><img src="js/help.png" id="gnuplot_help_icon" class="icon-image" alt="?" title="help"></td>
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
  
<table class="plot">
<tr><td>
    <canvas id="gnuplot_canvas" width="800" height="600" tabindex="0">
	Sorry, your browser seems not to support the HTML 5 canvas element
    </canvas>
</td></tr>
</table>
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
   
  <?php

  // getting job results

$query="SELECT * from JobResults where job_id=$job";
$job_result=mysql_query($query);

$i=0;
$num=mysql_numrows($job_result); 
$j=0;
$k=0;
$diff_res=array();
$res=array(); 
while ($i < $num) {
  $problem_id = mysql_result($job_result, $i, 'problem_id');
  // getting problem path and logic
  $query="SELECT * FROM Problems WHERE id=$problem_id";
  $problem=mysql_query($query);

  $problem_path=mysql_result($problem, 0, 'path');
  $index = strrpos($problem_path, "/");
  $problem_path=substr($problem_path,$index+1); 
  $problem_logic=mysql_result($problem, 0, 'logic'); 
	 
  $query="SELECT * FROM JobResults WHERE job_id=$reference_job and problem_id=$problem_id";
  $reference_result=mysql_query($query);
  $num_rows = mysql_num_rows($reference_result);
  if ($num_rows > 0) {
      
    $i_ref_result = mysql_result($reference_result, 0, 'result');
    $i_job_result = mysql_result($job_result, $i, 'result');

    if ($i_ref_result != $i_job_result) {
      // storing different results in a separate array
      $diff_res[$j]['problem_id']=$problem_id; 
      $diff_res[$j]['problem_path']=$problem_path;
      $diff_res[$j]['problem_logic']=$problem_logic;

      $diff_res[$j]['job_run_time']=mysql_result($job_result, $i, 'run_time');
      $diff_res[$j]['job_memory']=mysql_result($job_result, $i, 'memory');
      $diff_res[$j]['job_result']=$i_job_result;
      $diff_res[$j]['job_exit_status']=mysql_result($job_result, $i, 'exit_status');

      $diff_res[$j]['ref_run_time']=mysql_result($reference_result, 0, 'run_time');
      $diff_res[$j]['ref_memory']=mysql_result($reference_result, 0, 'memory');
      $diff_res[$j]['ref_result']=$i_ref_result;
      $diff_res[$j]['ref_exit_status']=mysql_result($reference_result, 0, 'exit_status');
      $j++; 
    } else {
      // storing results
      $res[$k]['problem_id']=$problem_id; 
      $res[$k]['problem_path']=$problem_path;
      $res[$k]['problem_logic']=$problem_logic;

      $res[$k]['job_run_time']=mysql_result($job_result, $i, 'run_time');
      $res[$k]['job_memory']=mysql_result($job_result, $i, 'memory');
      $res[$k]['job_result']=$i_job_result;
      $res[$k]['job_exit_status']=mysql_result($job_result, $i, 'exit_status');

      $res[$k]['ref_run_time']=mysql_result($reference_result, 0, 'run_time');
      $res[$k]['ref_memory']=mysql_result($reference_result, 0, 'memory');
      $res[$k]['ref_result']=$i_ref_result;
      $res[$k]['ref_exit_status']=mysql_result($reference_result, 0, 'exit_status');
      $k++; 
    }
  }
  $i++;
}
   
mysql_close();
?>

<h2> Different Results </h2>

<table class="sortable" border="1" cellpadding="5">
  <tr>
  <th> # </th>
  <th> Logic </th>
  <th> Benchmark </th>
  <th> Exit</th>
  <th> Time </th>
  <th> MB</th>
  <th> Result</th>
  <th> Ref Exit</th>
  <th> Ref Time </th>
  <th> Ref MB</th>
  <th> Ref Result</th>
  </tr>

  <?php
  $i = 0;
$num = count($diff_res);
while ($i < $num ) {
  ?>
    
  <tr>
    <td> <?php echo $i ?> </td>
    <td> <?php echo $diff_res[$i]['problem_logic'] ?> </td>
    <td> <?php echo $diff_res[$i]['problem_path'] ?> </td>

    <td> <?php echo $diff_res[$i]['job_exit_status'] ?> </td>
    <td> <?php echo $diff_res[$i]['job_run_time'] ?> </td>
    <td> <?php echo $diff_res[$i]['job_memory'] ?> </td>
    <td> <?php echo $diff_res[$i]['job_result'] ?> </td>

    <td> <?php echo $diff_res[$i]['ref_exit_status'] ?> </td>
    <td> <?php echo $diff_res[$i]['ref_run_time'] ?> </td>
    <td> <?php echo $diff_res[$i]['ref_memory'] ?> </td>
    <td> <?php echo $diff_res[$i]['ref_result'] ?> </td>
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
  <th> Logic </th>
  <th> Benchmark </th>
  <th> Exit</th>
  <th> Time </th>
  <th> MB</th>
  <th> Result</th>
  <th> Ref Exit</th>
  <th> Ref Time </th>
  <th> Ref MB</th>
  <th> Ref Result</th>
  </tr>

  <?php
  $i = 0;
$num = count($res);
while ($i < $num ) {
  ?>
    
  <tr>
    <td> <?php echo $i ?> </td>
    <td> <?php echo $res[$i]['problem_logic'] ?> </td>
    <td> <?php echo $res[$i]['problem_path'] ?> </td>

    <td> <?php echo $res[$i]['job_exit_status'] ?> </td>
    <td> <?php echo $res[$i]['job_run_time'] ?> </td>
    <td> <?php echo $res[$i]['job_memory'] ?> </td>
    <td> <?php echo $res[$i]['job_result'] ?> </td>

    <td> <?php echo $res[$i]['ref_exit_status'] ?> </td>
    <td> <?php echo $res[$i]['ref_run_time'] ?> </td>
    <td> <?php echo $res[$i]['ref_memory'] ?> </td>
    <td> <?php echo $res[$i]['ref_result'] ?> </td>
    </tr>

    <?php
    $i++; 
}
   
?>
</table>
</body>
</html>
