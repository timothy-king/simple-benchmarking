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

$job_ids=$_GET['job_ids'];

function generateCactusPlot($ids) {
  // make sure your system is set up to periodically clear the tmp directory
  $data_file = tempnam(sys_get_temp_dir(), "gnuplotdata");
  $js_plot_code = shell_exec('../scripts/cactusPlotWeb.py -j ' . $ids . ' -f ' . $data_file . ' | gnuplot');
  echo $js_plot_code;
}
echo "<script type=\"text/javascript\"> "; 
generateCactusPlot($job_ids);  
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
</div>
   

</body>
</html>
