var donotclosemenu = false;
var currentproc = null;
function plot(yArray, xArray, xlimits, ylimits, selmode, ytitle, plottitle, plotid)
{
    // Define Data
    const data = [{x: xArray, y: yArray, mode:selmode}];
    
    // Define Layout
    const layout = {xaxis: {range: xlimits, title: "Time"}, yaxis: {range: ylimits, title: ytitle},   title: plottitle};

    // Display using Plotly
    Plotly.newPlot(plotid, data, layout);
}

$(document).ready(function(){
    // sending a connect request to the server.
    var socket = io.connect('http://localhost:5000');

    socket.emit('host_list', {data: 'get_hosts'});

    socket.on('actualize_plots', function(msg, cb) { 
        //console.log("Active" , active)
        plot(msg.CPU_data, msg.time, msg.time_limit, msg.pc_limit, "lines", "Percentage", "CPU Usage", "plotCPU");
        plot(msg.RAM_data, msg.time, msg.time_limit, msg.pc_limit, "lines", "Percentage", "RAM Usage", "plotRAM");
        plot(msg.RDISK_data, msg.time, msg.time_limit, msg.rd_limit, "lines", "Mega Bytes", "Disk Reading Usage", "plotRDISK");
        plot(msg.WDISK_data, msg.time, msg.time_limit, msg.wd_limit, "lines", "Mega Bytes", "Disk Writing Usage", "plotWDISK");
       
        socket.emit('host_list', {data: 'get_hosts'});
    });

    socket.on('actualize_host_list', function(msg, cb) {    
        var current_host_list = []
        var new_host_list
        $.each($('#hostList').find('li'), function(i, val){ 
            current_host_list.push(val.firstChild.textContent);
        });
        new_host_list = msg.hosts.filter(n => !current_host_list.includes(n))

        $.each(new_host_list, function(i, val) {
            $('#hostList').append("<li id='h_" + i + "' class='h_" + i + "'>" + val + "<ul id='procList_h_" + i + "' class='list-off'></ul></li>");
        });
    });

    socket.on('actualize_proc_list', function(msg, cb) {    
        var current_proc_list = []
        var new_proc_list
        
        var listid = '#procList_' + msg.eid

        $.each($(listid).find('li'), function(i, val){ 
            current_proc_list.push(val.firstChild.textContent);
        });
        new_proc_list = msg.proc_list.filter(n => !current_proc_list.includes(n))
        
        $.each(new_proc_list, function(i, val) {
            $(listid).append("<li id='p_" + i + "' class='unselectechilds'>" + val + "</li>");
        });
        
        $(listid).attr("class", "list-on");
    });

    $('#hostList').on("click", "li", function(event){
        var parentid = "#" + $(this).parent().attr("id")
        var rmidlist = []
        var idtorm

        if(parentid == "#hostList")
        {
            if(!donotclosemenu)
            {
                if($("ul", this).attr("class") == "list-on")
                {
                    $("ul", this).attr("class", "list-off");
                    $(this).removeClass("liselected");
                }
                else if($("ul", this).attr("class") == "list-off")
                {
                    socket.emit('selected_host', {data: $(this).text(), eid: $(this).attr("id")});
                    $(this).addClass("liselected");
                }

                $.each($(parentid).find("li"), function(){
                    rmidlist.push($(this).attr("id"));
                }); 
                
                $.each(rmidlist, function(i, val) {
                    idtorm = "#" + val + " ul"
                    $(idtorm).attr("class", "list-off");
                    $(idtorm).empty();
                });  
            }
            else
            {
                donotclosemenu = false;
            }
        }
        else
        {   
            if(currentproc != null)
            {
                currentproc.removeClass("liselected");
                currentproc.addClass("unselectechilds");
                currentproc = $(this);
            }
            else
            {
                currentproc = $(this)
            }
            socket.emit('selected_proc', {data: $(this).text(), eid: $(this).attr("id")});
            donotclosemenu = true;
            currentproc.removeClass("unselectechilds");
            $(this).addClass("liselected");
        }
    });
});