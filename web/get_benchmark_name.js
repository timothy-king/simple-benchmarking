function benchmarkInit() {
    name = gnuplot.active_plot_name;
    if (document.getElementById("gnuplot_canvas")) {
	document.getElementById("gnuplot_canvas").onmousemove = updateBenchmarkName; 
    }
    gnuplot.mouse_update(); 
}

function updateBenchmarkName (event) {
    gnuplot.mouse_update(event); 
    if (document.getElementById(gnuplot.active_plot_name + "_benchmark")) {
     	x_value = document.getElementById(gnuplot.active_plot_name + "_x").innerHTML;
	y_value = document.getElementById(gnuplot.active_plot_name + "_y").innerHTML;
     	document.getElementById(gnuplot.active_plot_name + "_benchmark").innerHTML = getBenchmarkName(x_value, y_value); 
    }
}

function computeDifference(xval, yval, new_xval, new_yval) {
    var xdiff = xval - new_xval;
    var ydiff = yval - new_yval;
    var distance = Math.sqrt(Math.pow(xdiff, 2) + Math.pow(ydiff, 2));
    return distance; 
}

function getBenchmarkName(xvalue_str, yvalue_str) {
    var best_path = "";
    var best_point = -1; 
    var min_difference = 1;
    var xvalue = parseFloat(xvalue_str);
    var yvalue = parseFloat(yvalue_str);

    for (var i = 0; i < benchmark_paths.length; i++) {
	var new_xval = parseFloat(result_x_values[i]);
	var new_yval = parseFloat(result_y_values[i]);
	var diff = computeDifference(xvalue, yvalue, new_xval, new_yval);
	if (diff < min_difference) {
	    min_difference = diff;
	    best_point = i; 
	}
    }
    if (best_point != -1) {
	best_path = benchmark_paths[best_point]; 
    }
    return best_path;   
}