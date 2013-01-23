<html>
<head>
<script src="sorttable.js"></script>
   <link href="style.css" rel="stylesheet" type="text/css" media="screen" />
   </head>
   <body>


   <?php
$user=trim(file_get_contents("../config/user"));
$password=trim(file_get_contents("../config/password"));
$database="benchmarking";

$reference_job=$_GET['reference'];
$job=$_GET['job'];
   
mysql_connect("localhost",$user,$password);
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
