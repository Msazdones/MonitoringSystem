var donotclosemenu = false;
var currentproc = null;
function plot(yArray, xArray, xlimits, ylimits, selmode, ytitle, plottitle, plotid, color)
{
    // Define Data
    const data = [{x: xArray, y: yArray, type:selmode}];
    
    // Define Layout
    const layout = {xaxis: {range: xlimits, title: "Time"}, yaxis: {range: ylimits, title: ytitle},   title: plottitle, colorway:[color], paper_bgcolor: "rgba(241,226,251,0)", plot_bgcolor: "rgba(241,226,251,0)"};

    //paper_bgcolor: "rgba(0,0,0,0", //background color of the chart container space
    //plot_bgcolor: "rgba(0,0,0,0)", //background color of plot area

    // Display using Plotly
    Plotly.newPlot(plotid, data, layout);
}

$(document).ready(function(){
    // sending a connect request to the server.
    var socket = io.connect('http://localhost:5000');

    socket.emit('host_list', {data: 'get_hosts'});

    socket.on('actualize_plots', function(msg, cb) { 
        //console.log("Active" , active)
        plot(msg.CPU_data, msg.time, msg.time_limit, msg.pc_limit, "lines", "Percentage", "CPU Usage", "plotCPU", "#FF0101");
        plot(msg.RAM_data, msg.time, msg.time_limit, msg.pc_limit, "lines", "Percentage", "RAM Usage", "plotRAM", "#0118FF");
        plot(msg.RDISK_data, msg.time, msg.time_limit, msg.rd_limit, "bar", "Mega Bytes", "Disk Reading Usage", "plotRDISK", "#E6C700");
        plot(msg.WDISK_data, msg.time, msg.time_limit, msg.wd_limit, "bar", "Mega Bytes", "Disk Writing Usage", "plotWDISK", "#00B020");
       
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
            $('#hostList').append("<li id='h_" + i + "' class='h_" + i + "'>" + val + "<ul id='procList_h_" + i + "''></ul></li>");
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
        
    });

    $('#hostList').on("click", "li", function(event){
        var parentid = "#" + $(this).parent().attr("id")
        var rmidlist = []
        var idtorm
        var curclick = $(this).attr("id")

        if(parentid == "#hostList")
        {
            if(!donotclosemenu)
            {
                if($(this).hasClass("liselected"))
                {
                    $(this).removeClass("liselected");
                }
                else
                {   
                    socket.emit('selected_host', {data: $(this).text(), eid: $(this).attr("id")});
                    $(this).addClass("liselected");
                }
                
                $.each($(parentid).find("li"), function(){
                    rmidlist.push($(this).attr("id"));
                }); 
                console.log(rmidlist)
                $.each(rmidlist, function(i, val) {
                    id = "#" + val
                    idtorm = id + " ul"

                    if(val != curclick)
                    {
                        $("#" + val).removeClass("liselected");
                    }
                    
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
            $('.selproc h2').text($(this).text())

            donotclosemenu = true;
            currentproc.removeClass("unselectechilds");
            $(this).addClass("liselected");
        }
    });

    $("#searchInputField").on("input", function() {
        var searchTerms = $(this).val().toLowerCase();
        $(".hostList li").each(function() {
          var hasMatch = searchTerms.length == 0 || $(this).text().toLowerCase().indexOf(searchTerms) >= 0;
          var listItem = $(this);
          listItem.toggle(hasMatch);
        });
    });
});