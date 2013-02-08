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

   
   </body>
   </html>
